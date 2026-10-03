/* @ds-bundle: {"format":4,"namespace":"OpenSupplyHubDesignSystem_69f06a","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Eyebrow","sourcePath":"components/core/Eyebrow.jsx"},{"name":"SpeechBubble","sourcePath":"components/core/SpeechBubble.jsx"},{"name":"Stat","sourcePath":"components/core/Stat.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"}],"sourceHashes":{"components/core/Button.jsx":"534cec2edce7","components/core/Card.jsx":"0cecdc0ec4aa","components/core/Eyebrow.jsx":"04dab46142bd","components/core/SpeechBubble.jsx":"af07e0eb9a89","components/core/Stat.jsx":"cf150541cbe0","components/core/Tag.jsx":"054e11e68efb"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.OpenSupplyHubDesignSystem_69f06a = window.OpenSupplyHubDesignSystem_69f06a || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Pill button in the OSH deck CTA style (e.g. "GET PRICING"). */
function Button({
  variant = 'primary',
  size = 'md',
  children,
  ...rest
}) {
  const palettes = {
    primary: {
      background: 'var(--osh-off-black)',
      color: 'var(--osh-off-white)',
      border: '1.5px solid var(--osh-off-black)'
    },
    accent: {
      background: 'var(--osh-purple)',
      color: 'var(--osh-off-white)',
      border: '1.5px solid var(--osh-purple)'
    },
    outline: {
      background: 'transparent',
      color: 'var(--osh-off-black)',
      border: '1.5px solid var(--osh-off-black)'
    },
    inverse: {
      background: 'var(--osh-off-white)',
      color: 'var(--osh-off-black)',
      border: '1.5px solid var(--osh-off-white)'
    }
  };
  const sizes = {
    sm: {
      fontSize: 12,
      padding: '8px 20px'
    },
    md: {
      fontSize: 14,
      padding: '12px 28px'
    },
    lg: {
      fontSize: 16,
      padding: '16px 36px'
    }
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    style: {
      fontFamily: 'var(--font-body)',
      fontWeight: 700,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      borderRadius: 'var(--radius-pill)',
      cursor: 'pointer',
      ...palettes[variant],
      ...sizes[size]
    },
    onMouseEnter: e => {
      e.currentTarget.style.opacity = '0.85';
    },
    onMouseLeave: e => {
      e.currentTarget.style.opacity = '1';
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Flat content card — white surface, 16px radius, optional off-black keyline. No shadow. */
function Card({
  tone = 'white',
  keyline = false,
  padding = 32,
  children,
  style,
  ...rest
}) {
  const tones = {
    white: {
      background: 'var(--surface-card)'
    },
    offwhite: {
      background: 'var(--surface-page)'
    },
    dark: {
      background: 'var(--surface-page-dark)',
      color: 'var(--text-inverse)'
    },
    yellow: {
      background: 'var(--osh-yellow)'
    },
    greenTint: {
      background: 'var(--osh-green-tint)'
    }
  };
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      borderRadius: 'var(--radius-card)',
      border: keyline ? 'var(--border-keyline)' : 'none',
      padding,
      fontFamily: 'var(--font-body)',
      ...tones[tone],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/Eyebrow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Uppercase tracked kicker label, e.g. "CASE STUDY", "FEATURES: OS HUB SOLUTIONS". */
function Eyebrow({
  color = 'var(--osh-off-black)',
  children,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      fontFamily: 'var(--font-body)',
      textTransform: 'uppercase',
      letterSpacing: 'var(--tracking-eyebrow)',
      fontWeight: 700,
      fontSize: 'var(--text-eyebrow)',
      color
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Eyebrow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Eyebrow.jsx", error: String((e && e.message) || e) }); }

// components/core/SpeechBubble.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Rounded speech-bubble callout with a solid brand fill and off-black outline. */
function SpeechBubble({
  color = 'yellow',
  children,
  style,
  ...rest
}) {
  const fills = {
    yellow: 'var(--osh-yellow)',
    pink: 'var(--osh-pink)',
    green: 'var(--osh-green)',
    white: 'var(--osh-white)'
  };
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      position: 'relative',
      display: 'inline-block',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      background: fills[color],
      border: '2px solid var(--osh-off-black)',
      borderRadius: 28,
      padding: '18px 26px',
      fontFamily: 'var(--font-body)',
      fontWeight: 500,
      fontSize: 18,
      color: 'var(--osh-off-black)',
      lineHeight: 1.35
    }
  }, children), /*#__PURE__*/React.createElement("svg", {
    width: "34",
    height: "26",
    viewBox: "0 0 34 26",
    style: {
      position: 'absolute',
      left: 34,
      bottom: -22
    },
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M2 2 C10 2 22 2 30 2 L14 24 C13 14 8 6 2 2 Z",
    fill: fills[color],
    stroke: "var(--osh-off-black)",
    strokeWidth: "2",
    strokeLinejoin: "round"
  })));
}
Object.assign(__ds_scope, { SpeechBubble });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/SpeechBubble.jsx", error: String((e && e.message) || e) }); }

// components/core/Stat.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Big-number stat callout, e.g. "2,500,000+ / Production locations listed". */
function Stat({
  value,
  label,
  sublabel,
  color = 'var(--osh-purple)',
  align = 'center',
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      textAlign: align,
      fontFamily: 'var(--font-body)'
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontWeight: 800,
      fontSize: 72,
      lineHeight: 0.9,
      color
    }
  }, value), /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 700,
      fontSize: 20,
      marginTop: 8,
      color: 'var(--text-body)'
    }
  }, label), sublabel ? /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 15,
      marginTop: 4,
      color: 'var(--text-muted)'
    }
  }, sublabel) : null);
}
Object.assign(__ds_scope, { Stat });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Stat.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Small solid tag/chip for stakeholder groups and category labels. */
function Tag({
  color = 'yellow',
  children,
  ...rest
}) {
  const fills = {
    yellow: {
      background: 'var(--osh-yellow)',
      color: 'var(--osh-off-black)'
    },
    purple: {
      background: 'var(--osh-purple)',
      color: 'var(--osh-off-white)'
    },
    green: {
      background: 'var(--osh-green)',
      color: 'var(--osh-off-black)'
    },
    pink: {
      background: 'var(--osh-pink)',
      color: 'var(--osh-off-black)'
    },
    dark: {
      background: 'var(--osh-off-black)',
      color: 'var(--osh-off-white)'
    },
    outline: {
      background: 'transparent',
      color: 'var(--osh-off-black)',
      border: '1.5px solid var(--osh-off-black)'
    }
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-block',
      fontFamily: 'var(--font-body)',
      fontWeight: 700,
      fontSize: 13,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      padding: '5px 14px',
      borderRadius: 'var(--radius-pill)',
      ...fills[color]
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Eyebrow = __ds_scope.Eyebrow;

__ds_ns.SpeechBubble = __ds_scope.SpeechBubble;

__ds_ns.Stat = __ds_scope.Stat;

__ds_ns.Tag = __ds_scope.Tag;

})();
