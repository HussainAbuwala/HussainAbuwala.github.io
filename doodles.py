"""Hand-drawn line doodles for the "Outside work" strip on the home page.

Each is an SVG body on a 0 0 80 64 canvas. Ink lines use class "ink";
the one coloured part of each doodle uses class "acc" plus a palette class
(rust, ochre or slate), the colours of the film Everything Has a Price.
The cartoons doodle is deliberately generic: no trademarked characters.
"""

DOODLES = {
    # bat at an angle, ball beside it
    "cricket": '''
<g transform="rotate(-28 36 34)">
  <rect class="ink" x="33" y="4" width="6" height="15" rx="2"/>
  <path class="ink" d="M30 20 Q36 17 42 20 L43 54 Q36 59 29 54 Z"/>
  <path class="ink" d="M36 22 L36 51"/>
</g>
<circle class="acc rust" cx="62" cy="50" r="6.5"/>
<path class="acc rust" d="M57 46 Q62 50 67 46 M57 54 Q62 50 67 54"/>''',

    "basketball": '''
<circle class="ink" cx="40" cy="32" r="23"/>
<path class="acc ochre" d="M40 9 L40 55 M17 32 L63 32"/>
<path class="acc ochre" d="M24 15 Q34 32 24 49 M56 15 Q46 32 56 49"/>''',

    # shuttlecock, feathers up
    "badminton": '''
<path class="ink" d="M33 47 Q40 60 47 47 Z"/>
<path class="ink" d="M33 47 L25 13 M37 47 L34 11 M43 47 L46 11 M47 47 L55 13"/>
<path class="ink" d="M25 13 Q40 6 55 13"/>
<path class="acc slate" d="M29 31 Q40 27 51 31"/>''',

    # a small stack, one book in colour
    "books": '''
<rect class="ink" x="16" y="45" width="48" height="10" rx="1.5"/>
<rect class="acc rust" x="21" y="35" width="40" height="10" rx="1.5"/>
<path class="ink" d="M17 34 L60 30 L61 22 L18 26 Z"/>
<path class="ink" d="M24 50 L56 50 M27 40 L55 40"/>''',

    # a television showing a globe
    "news": '''
<rect class="ink" x="13" y="10" width="54" height="38" rx="4"/>
<circle class="acc slate" cx="40" cy="29" r="12"/>
<ellipse class="acc slate" cx="40" cy="29" rx="5" ry="12"/>
<path class="acc slate" d="M28 29 L52 29"/>
<path class="ink" d="M32 48 L28 56 M48 48 L52 56 M24 56 L56 56"/>''',

    # a plain t-shirt with a small "no logo" mark
    "tshirt": '''
<path class="ink" d="M29 9 L18 15 L9 28 L19 34 L23 28 L23 57 L57 57 L57 28 L61 34 L71 28 L62 15 L51 9 Q40 18 29 9 Z"/>
<circle class="acc rust" cx="49" cy="27" r="4.5"/>
<path class="acc rust" d="M46 30 L52 24"/>''',

    # a monitor with a code sign on the screen
    "computer": '''
<rect class="ink" x="13" y="8" width="54" height="36" rx="3"/>
<path class="acc slate" d="M33 21 L27 26 L33 31 M47 21 L53 26 L47 31 M43 19 L37 33"/>
<path class="ink" d="M36 44 L34 52 M44 44 L46 52 M26 53 L54 53"/>''',

    # an old television with rabbit ears, and a spinning top beside it
    "cartoons": '''
<rect class="ink" x="8" y="24" width="44" height="32" rx="6"/>
<rect class="ink" x="13" y="29" width="26" height="22" rx="4"/>
<circle class="ink" cx="46" cy="34" r="2.2"/>
<circle class="ink" cx="46" cy="44" r="2.2"/>
<path class="ink" d="M30 24 L20 9 M30 24 L40 9"/>
<path class="acc ochre" d="M60 47 Q67 41 74 47 L67 59 Z"/>
<path class="acc ochre" d="M67 41 L67 37"/>
<path class="acc rust" d="M58 56 Q67 62 76 56"/>''',
}
