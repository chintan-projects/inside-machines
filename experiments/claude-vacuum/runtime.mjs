// Trusted, actual Anatomy modules. The model only authors the local figure.
import * as k from '../../vendor/anatomy/kit/iso-kit.mjs';
import * as G from '../../vendor/anatomy/kit/lathe.mjs';
import * as T from '../../vendor/anatomy/kit/tube.mjs';
import {bagWindow, bagWindowAlpha} from './bag-window.mjs';
window.Anatomy = Object.freeze({k, G, T});
window.AnatomyTeaching = Object.freeze({bagWindow, bagWindowAlpha});
