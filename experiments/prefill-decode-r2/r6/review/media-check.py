"""Verify delivered AV, caption text, timing and the exact frozen source binding."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EPISODE = ROOT / 'video/production/episodes/ep01'
RECORD = sorted((EPISODE / 'delivery-records').iterdir())[-1]
metadata = json.loads((RECORD / 'metadata.json').read_text())
timeline = json.loads((RECORD / 'timeline.json').read_text())
video = ROOT / 'video' / metadata['files']['video_file_name']
srt = ROOT / 'video' / metadata['files']['subtitles'][0]['file_name']
probe = json.loads(subprocess.run(
    ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)],
    check=True, capture_output=True, text=True,
).stdout)
vstream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
astream = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
assert (vstream['width'], vstream['height']) == (1920, 1080)
assert astream['codec_name'] == 'aac' and int(astream['sample_rate']) == 48000
assert abs(float(probe['format']['duration']) - timeline['duration_seconds']) < .2


def seconds(value: str) -> float:
    """Parse an SRT or WebVTT timestamp."""
    h, m, s = value.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def cues(value: str) -> list[dict[str, str | float]]:
    """Read timed caption blocks without changing their words."""
    result = []
    for block in re.split(r'\n\s*\n', value.strip()):
        lines = block.splitlines()
        index = next((i for i, line in enumerate(lines) if ' --> ' in line), None)
        if index is None:
            continue
        start, end = lines[index].split(' --> ')
        result.append({'start': seconds(start), 'end': seconds(end),
                       'text': ' '.join(lines[index + 1:])})
    return result


captions = cues(srt.read_text())
assert captions and all(0 <= c['start'] < c['end'] <= timeline['duration_seconds'] + .1 for c in captions)
assert all(captions[i]['start'] >= captions[i - 1]['end'] - .001 for i in range(1, len(captions)))
source = json.loads((ROOT / 'video/production/shared/narration.json').read_text())
beats = [b for scene in source['scenes'] for b in scene['beats']]
normalize = lambda s: re.sub(r'\s+', ' ', s).strip()
expected = normalize(' '.join(b['narration'] for b in beats))
observed = normalize(' '.join(str(c['text']) for c in captions))
assert observed == expected, 'Delivered captions must preserve every frozen narration word.'
voice = yaml.safe_load((EPISODE / 'narration/narration.yaml').read_text())
by_id = {b['id']: b['narration'] for b in beats}
assert len(voice['beats']) == len(by_id) == 174
assert all(b['spoken_text'] == by_id[b['beat_id']] for b in voice['beats'])
assert (RECORD / 'script.yaml').read_bytes() == (EPISODE / 'script.yaml').read_bytes()
sha = hashlib.sha256((EPISODE / 'script.yaml').read_bytes()).hexdigest()
assert json.loads((ROOT / 'review/core-readiness.json').read_text())['script_sha256'] == sha
vtt = ROOT / 'review-site/captions.vtt'
assert cues(vtt.read_text()) == captions
result = {'script_sha256': sha, 'video_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
          'duration_seconds': timeline['duration_seconds'], 'narration_beats': len(beats),
          'caption_cues': len(captions), 'all_caption_words_match_frozen_script': True,
          'srt_vtt_text_and_timestamps_identical': True,
          'all_caption_times_valid_and_nonoverlapping': True,
          'video_dimensions': [1920, 1080], 'audio_codec': 'aac', 'audio_sample_rate': 48000,
          'delivered_script_matches_gate': True}
(ROOT / 'review/media-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
