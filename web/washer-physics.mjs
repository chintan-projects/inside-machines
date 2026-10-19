/**
 * Idealized contact at the top of a drum: N/m + g = omega^2 r.
 * No cloth, adhesion, water or friction simulation is claimed.
 * @param {number} rpm
 * @param {number} radius Illustrative radius in metres.
 */
export function spinContact(rpm, radius = .25) {
  if (!Number.isFinite(rpm) || !Number.isFinite(radius) || rpm < 0 || radius <= 0) throw new RangeError('Speed and radius must be finite, with nonnegative speed and positive radius.');
  const gravity = 9.81;
  const omega = rpm * 2 * Math.PI / 60;
  const acceleration = omega ** 2 * radius;
  const criticalRpm = Math.sqrt(gravity / radius) * 60 / (2 * Math.PI);
  return { rpm, radius, gravity, acceleration, criticalRpm,
    contact: acceleration >= gravity - 1e-12,
    normalPerKg: Math.max(0, acceleration - gravity) };
}
