from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiagramResult:
    svg: Optional[str] = None
    ascii: Optional[str] = None
    description: Optional[str] = None
    jsxgraph_code: Optional[str] = None


class DiagramGenerator:
    """
    Diagram generator that produces JSXGraph JavaScript code for interactive
    math visualizations. Falls back to SVG for non-geometric concepts.

    JSXGraph code format: Pure JS using `board` and `JXG` variables.
    The board is already initialized by the HTML template — code only creates elements.
    """

    # Map of keywords to JSXGraph generator methods
    JSXGRAPH_TEMPLATES = {
        "right triangle": "_jsx_right_triangle",
        "pythagoras": "_jsx_right_triangle",
        "right-angled": "_jsx_right_triangle",
        "hypotenuse": "_jsx_right_triangle",
        "circle with tangent": "_jsx_circle_tangent",
        "tangent": "_jsx_circle_tangent",
        "circle": "_jsx_circle",
        "radius": "_jsx_circle",
        "quadratic": "_jsx_parabola",
        "parabola": "_jsx_parabola",
        "linear equation": "_jsx_linear_graph",
        "straight line": "_jsx_linear_graph",
        "y = mx": "_jsx_linear_graph",
        "coordinate": "_jsx_coordinate_plane",
        "triangle": "_jsx_triangle",
        "trigonometry": "_jsx_trig_triangle",
        "sin": "_jsx_trig_triangle",
        "cos": "_jsx_trig_triangle",
        "tan": "_jsx_trig_triangle",
        "angle": "_jsx_angle",
        "number line": "_jsx_number_line",
    }

    async def generate(self, description: str, style: str, language: str) -> DiagramResult:
        cleaned = description.strip().lower()
        if not cleaned:
            return DiagramResult()

        # Find matching JSXGraph template
        for keyword, method_name in self.JSXGRAPH_TEMPLATES.items():
            if keyword in cleaned:
                method = getattr(self, method_name)
                jsx_code = method(description.strip())
                return DiagramResult(
                    jsxgraph_code=jsx_code,
                    description=description.strip(),
                )

        # Fallback: simple labeled SVG for non-geometric content
        svg = self._svg_fallback(description.strip())
        return DiagramResult(svg=svg, description=description.strip())

    # =========================================================================
    # JSXGraph Templates (pure JS using `board` and `JXG`)
    # =========================================================================

    def _jsx_right_triangle(self, desc: str) -> str:
        return """
// Pythagoras Theorem: Right Triangle
var A = board.create('point', [0, 0], {name: 'A', size: 3, color: '#2563eb', fixed: true});
var B = board.create('point', [4, 0], {name: 'B', size: 3, color: '#2563eb', fixed: true});
var C = board.create('point', [0, 3], {name: 'C', size: 3, color: '#2563eb', fixed: true});

// Triangle sides
board.create('segment', [A, B], {strokeColor: '#16a34a', strokeWidth: 2.5});
board.create('segment', [B, C], {strokeColor: '#dc2626', strokeWidth: 2.5});
board.create('segment', [C, A], {strokeColor: '#2563eb', strokeWidth: 2.5});

// Right angle marker
board.create('angle', [B, A, C], {radius: 0.4, type: 'square', fillColor: '#fef3c7', strokeColor: '#dc2626'});

// Side labels
board.create('text', [2, -0.5, 'Base (b) = 4'], {fontSize: 14, color: '#16a34a', anchorX: 'middle'});
board.create('text', [-0.8, 1.5, 'Height (a) = 3'], {fontSize: 14, color: '#2563eb', anchorX: 'middle'});
board.create('text', [2.5, 2, 'Hypotenuse (c) = 5'], {fontSize: 14, color: '#dc2626', anchorX: 'middle'});

// Formula
board.create('text', [2, 4, 'a² + b² = c²'], {fontSize: 18, color: '#1e40af', anchorX: 'middle', cssClass: 'formula'});
board.create('text', [2, 3.4, '3² + 4² = 9 + 16 = 25 = 5²  ✓'], {fontSize: 14, color: '#16a34a', anchorX: 'middle'});
"""

    def _jsx_circle(self, desc: str) -> str:
        return """
// Circle: Radius, Diameter, Area & Circumference
var O = board.create('point', [0, 0], {name: 'O (Center)', size: 4, color: '#dc2626', fixed: true});
var P = board.create('point', [3, 0], {name: 'P', size: 3, color: '#2563eb'});

// Circle
var circle = board.create('circle', [O, P], {strokeColor: '#2563eb', strokeWidth: 2.5, fillColor: '#eff6ff', fillOpacity: 0.3});

// Radius line
board.create('segment', [O, P], {strokeColor: '#16a34a', strokeWidth: 2, dash: 2});
board.create('text', [1.5, 0.4, 'r'], {fontSize: 16, color: '#16a34a', fontWeight: 'bold'});

// Diameter line
var Q = board.create('point', [-3, 0], {name: 'Q', size: 3, color: '#9333ea', fixed: true});
board.create('segment', [Q, P], {strokeColor: '#9333ea', strokeWidth: 1.5, dash: 3});
board.create('text', [0, -0.6, 'd = 2r'], {fontSize: 13, color: '#9333ea', anchorX: 'middle'});

// Formulas
board.create('text', [0, 4.5, 'Area = πr²'], {fontSize: 16, color: '#1e40af', anchorX: 'middle'});
board.create('text', [0, 3.8, 'Circumference = 2πr'], {fontSize: 16, color: '#1e40af', anchorX: 'middle'});
"""

    def _jsx_circle_tangent(self, desc: str) -> str:
        return """
// Circle with Tangent: Radius ⊥ Tangent at point of contact
var O = board.create('point', [0, 0], {name: 'O', size: 4, color: '#dc2626', fixed: true});
var circle = board.create('circle', [O, 3], {strokeColor: '#2563eb', strokeWidth: 2.5, fillColor: '#eff6ff', fillOpacity: 0.2});

// Point of tangency
var P = board.create('point', [3, 0], {name: 'P (Point of Contact)', size: 4, color: '#f59e0b', fixed: true});

// Radius to tangent point
board.create('segment', [O, P], {strokeColor: '#16a34a', strokeWidth: 2});
board.create('text', [1.5, 0.4, 'r'], {fontSize: 15, color: '#16a34a', fontWeight: 'bold'});

// Tangent line (vertical through P)
var T1 = board.create('point', [3, 4], {visible: false});
var T2 = board.create('point', [3, -4], {visible: false});
board.create('segment', [T1, T2], {strokeColor: '#dc2626', strokeWidth: 2.5, name: 'Tangent'});
board.create('text', [3.5, 3, 'Tangent line'], {fontSize: 14, color: '#dc2626'});

// Right angle marker at P
board.create('angle', [T1, P, O], {radius: 0.4, type: 'square', fillColor: '#fef3c7', strokeColor: '#dc2626'});
board.create('text', [2.3, -0.4, '90°'], {fontSize: 13, color: '#dc2626'});

// Key theorem
board.create('text', [0, 4.5, 'Radius ⊥ Tangent at point of contact'], {fontSize: 15, color: '#1e40af', anchorX: 'middle', fontWeight: 'bold'});
"""

    def _jsx_parabola(self, desc: str) -> str:
        return """
// Quadratic Equation: y = ax² + bx + c (Parabola)
// Interactive: drag vertex to see equation change
var vertex = board.create('point', [0, -2], {name: 'Vertex', size: 4, color: '#dc2626'});

// Parabola through vertex
var parabola = board.create('functiongraph', [function(x) {
    var h = vertex.X();
    var k = vertex.Y();
    return (x - h) * (x - h) + k;
}], {strokeColor: '#dc2626', strokeWidth: 2.5});

// Roots (where parabola crosses x-axis)
board.create('text', [0, 5, 'y = (x-h)² + k  (Drag the vertex!)'], {fontSize: 15, color: '#1e40af', anchorX: 'middle', fontWeight: 'bold'});
board.create('text', [0, 4.3, 'Parabola opens upward when a > 0'], {fontSize: 13, color: '#64748b', anchorX: 'middle'});

// Axis of symmetry
board.create('line', [[function(){return vertex.X();}, 0], [function(){return vertex.X();}, 1]], {
    strokeColor: '#9333ea', strokeWidth: 1, dash: 3, name: 'Axis of symmetry'
});
"""

    def _jsx_linear_graph(self, desc: str) -> str:
        return """
// Linear Equation: y = mx + c
// Interactive: drag points to change slope and intercept
var A = board.create('point', [0, 2], {name: 'y-intercept (c=2)', size: 4, color: '#2563eb'});
var B = board.create('point', [3, 5], {name: '', size: 4, color: '#16a34a'});

// Line through the two points
var line = board.create('line', [A, B], {strokeColor: '#dc2626', strokeWidth: 2.5});

// Slope triangle
var C = board.create('point', [function(){return B.X();}, function(){return A.Y();}], {visible: false});
board.create('segment', [A, C], {strokeColor: '#16a34a', strokeWidth: 1.5, dash: 2});
board.create('segment', [C, B], {strokeColor: '#f59e0b', strokeWidth: 1.5, dash: 2});
board.create('text', [function(){return (A.X()+B.X())/2;}, function(){return A.Y()-0.4;}, 'run'], {fontSize: 13, color: '#16a34a'});
board.create('text', [function(){return B.X()+0.3;}, function(){return (A.Y()+B.Y())/2;}, 'rise'], {fontSize: 13, color: '#f59e0b'});

// Dynamic slope display
board.create('text', [-4, 5, function() {
    var m = (B.Y() - A.Y()) / (B.X() - A.X());
    return 'slope (m) = ' + m.toFixed(2);
}], {fontSize: 14, color: '#1e40af'});

board.create('text', [-4, 4.2, function() {
    return 'y = mx + c (Drag the points!)';
}], {fontSize: 14, color: '#64748b'});
"""

    def _jsx_coordinate_plane(self, desc: str) -> str:
        return """
// Coordinate Geometry: The 4 Quadrants
// Interactive: click to see coordinates
board.create('text', [3, 3, 'Quadrant I\\n(+, +)'], {fontSize: 16, color: '#2563eb', anchorX: 'middle', fontWeight: 'bold'});
board.create('text', [-3, 3, 'Quadrant II\\n(-, +)'], {fontSize: 16, color: '#16a34a', anchorX: 'middle', fontWeight: 'bold'});
board.create('text', [-3, -3, 'Quadrant III\\n(-, -)'], {fontSize: 16, color: '#dc2626', anchorX: 'middle', fontWeight: 'bold'});
board.create('text', [3, -3, 'Quadrant IV\\n(+, -)'], {fontSize: 16, color: '#9333ea', anchorX: 'middle', fontWeight: 'bold'});

// Origin
board.create('point', [0, 0], {name: 'O (0,0)', size: 5, color: '#dc2626', fixed: true});

// Example points for students to understand
var P1 = board.create('point', [2, 3], {name: 'P(2,3)', size: 4, color: '#2563eb'});
var P2 = board.create('point', [-3, 2], {name: 'Q(-3,2)', size: 4, color: '#16a34a'});
var P3 = board.create('point', [-2, -2], {name: 'R(-2,-2)', size: 4, color: '#dc2626'});

board.create('text', [0, 5.5, 'Drag the points to explore coordinates!'], {fontSize: 14, color: '#64748b', anchorX: 'middle'});
"""

    def _jsx_triangle(self, desc: str) -> str:
        return """
// Triangle: Interactive with side & angle measurements
var A = board.create('point', [0, 0], {name: 'A', size: 4, color: '#dc2626'});
var B = board.create('point', [5, 0], {name: 'B', size: 4, color: '#dc2626'});
var C = board.create('point', [2, 4], {name: 'C', size: 4, color: '#dc2626'});

// Sides
board.create('segment', [A, B], {strokeColor: '#2563eb', strokeWidth: 2.5});
board.create('segment', [B, C], {strokeColor: '#16a34a', strokeWidth: 2.5});
board.create('segment', [C, A], {strokeColor: '#9333ea', strokeWidth: 2.5});

// Side length labels
board.create('text', [function(){return (A.X()+B.X())/2;}, function(){return (A.Y()+B.Y())/2-0.5;}, function(){
    var d = A.Dist(B); return 'a = ' + d.toFixed(1);
}], {fontSize: 13, color: '#2563eb'});

board.create('text', [function(){return (B.X()+C.X())/2+0.3;}, function(){return (B.Y()+C.Y())/2;}, function(){
    var d = B.Dist(C); return 'b = ' + d.toFixed(1);
}], {fontSize: 13, color: '#16a34a'});

board.create('text', [function(){return (C.X()+A.X())/2-0.5;}, function(){return (C.Y()+A.Y())/2;}, function(){
    var d = C.Dist(A); return 'c = ' + d.toFixed(1);
}], {fontSize: 13, color: '#9333ea'});

// Angles
board.create('angle', [B, A, C], {radius: 0.6, fillColor: '#dbeafe', name: function(){
    return this.Value !== undefined ? (this.Value() * 180 / Math.PI).toFixed(0) + '°' : '';
}});

board.create('text', [2.5, 5, 'Drag vertices to explore!'], {fontSize: 14, color: '#64748b', anchorX: 'middle'});
"""

    def _jsx_trig_triangle(self, desc: str) -> str:
        return """
// Trigonometric Ratios: sin, cos, tan
var A = board.create('point', [0, 0], {name: 'A', size: 4, color: '#334155', fixed: true});
var B = board.create('point', [5, 0], {name: 'B (Adjacent)', size: 4, color: '#334155', fixed: true});
var C = board.create('point', [5, 3], {name: 'C', size: 4, color: '#334155'});

// Triangle
board.create('polygon', [A, B, C], {fillColor: '#eff6ff', fillOpacity: 0.4,
    borders: {strokeColor: '#2563eb', strokeWidth: 2.5}});

// Right angle at B
board.create('angle', [A, B, C], {radius: 0.4, type: 'square', fillColor: '#fef3c7', strokeColor: '#dc2626'});

// Angle theta at A
board.create('angle', [B, A, C], {radius: 0.8, fillColor: '#fde68a', fillOpacity: 0.5, name: 'θ'});

// Side labels (dynamic)
board.create('text', [2.5, -0.6, function(){return 'Adjacent (B) = ' + A.Dist(B).toFixed(1);}], {fontSize: 13, color: '#16a34a', anchorX: 'middle'});
board.create('text', [5.8, 1.5, function(){return 'Opposite (P) = ' + B.Dist(C).toFixed(1);}], {fontSize: 13, color: '#dc2626'});
board.create('text', [2, 2.2, function(){return 'Hypotenuse (H) = ' + A.Dist(C).toFixed(1);}], {fontSize: 13, color: '#2563eb'});

// Ratio formulas
board.create('text', [-1, 5, function(){
    var opp = B.Dist(C), adj = A.Dist(B), hyp = A.Dist(C);
    return 'sin θ = P/H = ' + (opp/hyp).toFixed(3);
}], {fontSize: 14, color: '#dc2626'});
board.create('text', [-1, 4.3, function(){
    var opp = B.Dist(C), adj = A.Dist(B), hyp = A.Dist(C);
    return 'cos θ = B/H = ' + (adj/hyp).toFixed(3);
}], {fontSize: 14, color: '#16a34a'});
board.create('text', [-1, 3.6, function(){
    var opp = B.Dist(C), adj = A.Dist(B);
    return 'tan θ = P/B = ' + (opp/adj).toFixed(3);
}], {fontSize: 14, color: '#2563eb'});

board.create('text', [2, 5.5, 'Drag point C to see ratios change!'], {fontSize: 14, color: '#64748b', anchorX: 'middle'});
"""

    def _jsx_angle(self, desc: str) -> str:
        return """
// Angle measurement: Interactive
var O = board.create('point', [0, 0], {name: 'O (Vertex)', size: 4, color: '#dc2626', fixed: true});
var A = board.create('point', [5, 0], {name: 'A', size: 4, color: '#2563eb'});
var B = board.create('point', [3, 4], {name: 'B', size: 4, color: '#16a34a'});

// Rays
board.create('segment', [O, A], {strokeColor: '#2563eb', strokeWidth: 2.5});
board.create('segment', [O, B], {strokeColor: '#16a34a', strokeWidth: 2.5});

// Angle arc
var angle = board.create('angle', [A, O, B], {radius: 1.2, fillColor: '#fde68a', fillOpacity: 0.5,
    name: function(){ return (angle.Value() * 180 / Math.PI).toFixed(1) + '°'; }
});

board.create('text', [2.5, 5.5, 'Drag A or B to change the angle!'], {fontSize: 14, color: '#64748b', anchorX: 'middle'});
board.create('text', [2.5, 4.8, function(){
    var deg = angle.Value() * 180 / Math.PI;
    if (deg < 90) return 'This is an ACUTE angle (< 90°)';
    if (deg > 90 && deg < 180) return 'This is an OBTUSE angle (> 90°)';
    if (Math.abs(deg - 90) < 2) return 'This is a RIGHT angle (= 90°)';
    return 'Angle measurement: ' + deg.toFixed(1) + '°';
}], {fontSize: 13, color: '#1e40af', anchorX: 'middle'});
"""

    def _jsx_number_line(self, desc: str) -> str:
        return """
// Number Line
for (var i = -5; i <= 5; i++) {
    board.create('point', [i, 0], {name: String(i), size: 2, color: '#334155', fixed: true,
        label: {offset: [0, -15], fontSize: 13}});
}
board.create('line', [[-6, 0], [6, 0]], {strokeColor: '#334155', strokeWidth: 2, straightFirst: true, straightLast: true});

// Origin highlight
board.create('point', [0, 0], {name: 'Origin', size: 5, color: '#dc2626', fixed: true,
    label: {offset: [0, 15], fontSize: 14, color: '#dc2626'}});

// Draggable point for exploration
var P = board.create('point', [2.5, 0], {name: '', size: 6, color: '#2563eb',
    snapToGrid: true, attractors: [{X: function(){return Math.round(P.X());}, Y: function(){return 0;}}]});

board.create('text', [0, 1.5, function(){ return 'Point at: ' + P.X().toFixed(1); }],
    {fontSize: 15, color: '#2563eb', anchorX: 'middle'});
board.create('text', [0, 2.5, 'Drag the blue point along the number line!'],
    {fontSize: 13, color: '#64748b', anchorX: 'middle'});
"""

    def _svg_fallback(self, desc: str) -> str:
        """Fallback SVG for non-geometric concepts."""
        lines = []
        words = desc.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > 45:
                lines.append(current_line)
                current_line = word
            else:
                current_line = f"{current_line} {word}".strip()
        if current_line:
            lines.append(current_line)
        lines = lines[:5]

        text_elements = "".join(
            f'<text x="175" y="{100 + i * 22}" text-anchor="middle" font-family="Arial" font-size="13" fill="#334155">{self._escape_svg(line)}</text>'
            for i, line in enumerate(lines)
        )

        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="250" viewBox="0 0 350 250">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            '<rect x="10" y="10" width="330" height="230" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="6"/>'
            '<rect x="60" y="20" width="230" height="30" rx="6" fill="#e0f2fe"/>'
            '<text x="175" y="42" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#0369a1">Diagram</text>'
            f'{text_elements}'
            '</svg>'
        )

    def _escape_svg(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;")
        )
    """
    Diagram generator that produces actual SVG visuals for common math concepts.
    Uses template-based SVG generation for known diagram types,
    with a labeled fallback for unknown types.
    """

    # Map of keywords to diagram generator methods
    DIAGRAM_TEMPLATES = {
        "right triangle": "_svg_right_triangle",
        "pythagoras": "_svg_right_triangle",
        "right-angled": "_svg_right_triangle",
        "hypotenuse": "_svg_right_triangle",
        "circle": "_svg_circle",
        "tangent": "_svg_circle_tangent",
        "radius": "_svg_circle",
        "quadratic": "_svg_parabola",
        "parabola": "_svg_parabola",
        "linear equation": "_svg_linear_graph",
        "straight line": "_svg_linear_graph",
        "y = mx": "_svg_linear_graph",
        "coordinate": "_svg_coordinate_plane",
        "number line": "_svg_number_line",
        "triangle": "_svg_triangle",
        "angle": "_svg_angle",
        "trigonometry": "_svg_trig_triangle",
        "sin": "_svg_trig_triangle",
        "cos": "_svg_trig_triangle",
        "tan": "_svg_trig_triangle",
    }

    async def generate(self, description: str, style: str, language: str) -> DiagramResult:
        cleaned = description.strip().lower()
        if not cleaned:
            return DiagramResult()

        # Find matching template
        for keyword, method_name in self.DIAGRAM_TEMPLATES.items():
            if keyword in cleaned:
                method = getattr(self, method_name)
                svg = method(description.strip())
                return DiagramResult(svg=svg, description=description.strip())

        # Fallback: labeled diagram placeholder
        svg = self._svg_fallback(description.strip())
        return DiagramResult(svg=svg, description=description.strip())

    def _svg_right_triangle(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="300" viewBox="0 0 350 300">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Triangle
            '<polygon points="60,250 260,250 60,70" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
            # Right angle marker
            '<polyline points="60,220 90,220 90,250" fill="none" stroke="#dc2626" stroke-width="1.5"/>'
            # Labels
            '<text x="150" y="272" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#1e293b">Base (b)</text>'
            '<text x="35" y="165" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#1e293b" transform="rotate(-90 35 165)">Height (a)</text>'
            '<text x="175" y="148" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626" transform="rotate(-42 175 148)">Hypotenuse (c)</text>'
            # Formula
            '<rect x="60" y="10" width="230" height="35" rx="6" fill="#dbeafe"/>'
            '<text x="175" y="33" text-anchor="middle" font-family="Arial" font-size="15" font-weight="bold" fill="#1e40af">a² + b² = c²</text>'
            # Right angle label
            '<text x="78" y="240" font-family="Arial" font-size="11" fill="#dc2626">90°</text>'
            '</svg>'
        )

    def _svg_circle(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Circle
            '<circle cx="160" cy="160" r="100" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
            # Center point
            '<circle cx="160" cy="160" r="4" fill="#dc2626"/>'
            '<text x="168" y="155" font-family="Arial" font-size="12" fill="#dc2626">O</text>'
            # Radius line
            '<line x1="160" y1="160" x2="260" y2="160" stroke="#16a34a" stroke-width="2" stroke-dasharray="6,3"/>'
            '<text x="210" y="150" font-family="Arial" font-size="13" font-weight="bold" fill="#16a34a">r</text>'
            # Diameter
            '<line x1="60" y1="160" x2="260" y2="160" stroke="#9333ea" stroke-width="1.5" stroke-dasharray="4,4"/>'
            '<text x="145" y="180" font-family="Arial" font-size="12" fill="#9333ea">d = 2r</text>'
            # Formulas
            '<rect x="60" y="10" width="200" height="50" rx="6" fill="#dbeafe"/>'
            '<text x="160" y="30" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="#1e40af">Area = πr²</text>'
            '<text x="160" y="50" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="#1e40af">Circumference = 2πr</text>'
            '</svg>'
        )

    def _svg_circle_tangent(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="380" height="320" viewBox="0 0 380 320">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Circle
            '<circle cx="170" cy="160" r="90" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
            # Center
            '<circle cx="170" cy="160" r="4" fill="#dc2626"/>'
            '<text x="178" y="155" font-family="Arial" font-size="12" fill="#dc2626">O</text>'
            # Radius to tangent point
            '<line x1="170" y1="160" x2="260" y2="160" stroke="#16a34a" stroke-width="2"/>'
            '<text x="215" y="150" font-family="Arial" font-size="12" font-weight="bold" fill="#16a34a">r</text>'
            # Tangent point
            '<circle cx="260" cy="160" r="5" fill="#f59e0b"/>'
            '<text x="265" y="150" font-family="Arial" font-size="12" font-weight="bold" fill="#f59e0b">P</text>'
            # Tangent line
            '<line x1="260" y1="60" x2="260" y2="260" stroke="#dc2626" stroke-width="2.5"/>'
            '<text x="270" y="80" font-family="Arial" font-size="13" font-weight="bold" fill="#dc2626">Tangent</text>'
            # Right angle at tangent point
            '<polyline points="240,160 240,140 260,140" fill="none" stroke="#dc2626" stroke-width="1.5"/>'
            # Key fact
            '<rect x="40" y="10" width="300" height="35" rx="6" fill="#fef3c7"/>'
            '<text x="190" y="33" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="#92400e">Radius ⊥ Tangent at point of contact</text>'
            # Label 90 degrees
            '<text x="235" y="172" font-family="Arial" font-size="11" fill="#dc2626">90°</text>'
            '</svg>'
        )

    def _svg_parabola(self, desc: str) -> str:
        # Generate parabola points for y = x^2 (scaled)
        points = []
        for i in range(-8, 9):
            x = 175 + i * 12
            y = 240 - (i * i) * 2.2
            points.append(f"{x},{y}")
        path = " ".join(points)
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="300" viewBox="0 0 350 300">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Axes
            '<line x1="30" y1="250" x2="320" y2="250" stroke="#64748b" stroke-width="1.5"/>'
            '<line x1="175" y1="280" x2="175" y2="20" stroke="#64748b" stroke-width="1.5"/>'
            # Arrow heads
            '<polygon points="320,250 312,245 312,255" fill="#64748b"/>'
            '<polygon points="175,20 170,28 180,28" fill="#64748b"/>'
            # Axis labels
            '<text x="325" y="255" font-family="Arial" font-size="13" fill="#334155">x</text>'
            '<text x="180" y="18" font-family="Arial" font-size="13" fill="#334155">y</text>'
            # Parabola curve
            f'<polyline points="{path}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            # Vertex label
            '<circle cx="175" cy="240" r="4" fill="#2563eb"/>'
            '<text x="182" y="260" font-family="Arial" font-size="11" fill="#2563eb">Vertex</text>'
            # Title
            '<rect x="70" y="5" width="210" height="30" rx="6" fill="#dbeafe"/>'
            '<text x="175" y="25" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="#1e40af">y = ax² + bx + c (Parabola)</text>'
            # Origin
            '<text x="178" y="266" font-family="Arial" font-size="11" fill="#64748b">O</text>'
            '</svg>'
        )

    def _svg_linear_graph(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="300" viewBox="0 0 350 300">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Grid lines
            '<g stroke="#e2e8f0" stroke-width="0.5">'
            '<line x1="80" y1="250" x2="80" y2="30"/><line x1="130" y1="250" x2="130" y2="30"/>'
            '<line x1="180" y1="250" x2="180" y2="30"/><line x1="230" y1="250" x2="230" y2="30"/>'
            '<line x1="280" y1="250" x2="280" y2="30"/>'
            '<line x1="30" y1="80" x2="320" y2="80"/><line x1="30" y1="130" x2="320" y2="130"/>'
            '<line x1="30" y1="180" x2="320" y2="180"/><line x1="30" y1="230" x2="320" y2="230"/>'
            '</g>'
            # Axes
            '<line x1="30" y1="250" x2="320" y2="250" stroke="#64748b" stroke-width="1.5"/>'
            '<line x1="30" y1="280" x2="30" y2="20" stroke="#64748b" stroke-width="1.5"/>'
            # Line y = 2x + 1
            '<line x1="30" y1="230" x2="280" y2="30" stroke="#dc2626" stroke-width="2.5"/>'
            # Slope triangle
            '<line x1="130" y1="150" x2="230" y2="150" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="5,3"/>'
            '<line x1="230" y1="150" x2="230" y2="70" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="5,3"/>'
            '<text x="170" y="168" font-family="Arial" font-size="11" fill="#16a34a">run</text>'
            '<text x="235" y="115" font-family="Arial" font-size="11" fill="#16a34a">rise</text>'
            # Labels
            '<text x="325" y="255" font-family="Arial" font-size="13" fill="#334155">x</text>'
            '<text x="20" y="18" font-family="Arial" font-size="13" fill="#334155">y</text>'
            # Title
            '<rect x="80" y="5" width="200" height="30" rx="6" fill="#dbeafe"/>'
            '<text x="180" y="25" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="#1e40af">y = mx + c (Straight Line)</text>'
            # Slope label
            '<text x="150" y="290" text-anchor="middle" font-family="Arial" font-size="12" fill="#334155">slope (m) = rise / run</text>'
            '</svg>'
        )

    def _svg_coordinate_plane(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Grid
            '<g stroke="#e2e8f0" stroke-width="0.5">'
            + ''.join(f'<line x1="{40+i*40}" y1="20" x2="{40+i*40}" y2="300"/>' for i in range(7))
            + ''.join(f'<line x1="20" y1="{40+i*40}" x2="300" y2="{40+i*40}"/>' for i in range(7))
            + '</g>'
            # Axes
            '<line x1="160" y1="20" x2="160" y2="300" stroke="#334155" stroke-width="2"/>'
            '<line x1="20" y1="160" x2="300" y2="160" stroke="#334155" stroke-width="2"/>'
            # Quadrant labels
            '<text x="220" y="80" font-family="Arial" font-size="16" font-weight="bold" fill="#2563eb">I (+,+)</text>'
            '<text x="60" y="80" font-family="Arial" font-size="16" font-weight="bold" fill="#16a34a">II (-,+)</text>'
            '<text x="55" y="230" font-family="Arial" font-size="16" font-weight="bold" fill="#dc2626">III (-,-)</text>'
            '<text x="215" y="230" font-family="Arial" font-size="16" font-weight="bold" fill="#9333ea">IV (+,-)</text>'
            # Origin
            '<circle cx="160" cy="160" r="4" fill="#dc2626"/>'
            '<text x="165" y="178" font-family="Arial" font-size="12" font-weight="bold" fill="#334155">O(0,0)</text>'
            # Axis names
            '<text x="285" y="155" font-family="Arial" font-size="14" font-weight="bold" fill="#334155">X</text>'
            '<text x="165" y="35" font-family="Arial" font-size="14" font-weight="bold" fill="#334155">Y</text>'
            '</svg>'
        )

    def _svg_number_line(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100" viewBox="0 0 400 100">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            '<line x1="20" y1="50" x2="380" y2="50" stroke="#334155" stroke-width="2"/>'
            '<polygon points="380,50 372,45 372,55" fill="#334155"/>'
            + ''.join(
                f'<line x1="{60+i*40}" y1="42" x2="{60+i*40}" y2="58" stroke="#334155" stroke-width="1.5"/>'
                f'<text x="{60+i*40}" y="75" text-anchor="middle" font-family="Arial" font-size="12" fill="#334155">{i-3}</text>'
                for i in range(8)
            )
            + '<circle cx="180" cy="50" r="5" fill="#dc2626"/>'
            '<text x="180" y="35" text-anchor="middle" font-family="Arial" font-size="11" fill="#dc2626">Origin</text>'
            '</svg>'
        )

    def _svg_triangle(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="280" viewBox="0 0 350 280">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            '<polygon points="175,40 60,240 290,240" fill="none" stroke="#2563eb" stroke-width="2.5"/>'
            '<circle cx="175" cy="40" r="4" fill="#dc2626"/>'
            '<text x="175" y="30" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626">A</text>'
            '<circle cx="60" cy="240" r="4" fill="#dc2626"/>'
            '<text x="45" y="255" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626">B</text>'
            '<circle cx="290" cy="240" r="4" fill="#dc2626"/>'
            '<text x="300" y="255" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626">C</text>'
            # Side labels
            '<text x="105" y="135" text-anchor="middle" font-family="Arial" font-size="13" fill="#16a34a" transform="rotate(-60 105 135)">c</text>'
            '<text x="245" y="135" text-anchor="middle" font-family="Arial" font-size="13" fill="#16a34a" transform="rotate(60 245 135)">b</text>'
            '<text x="175" y="262" text-anchor="middle" font-family="Arial" font-size="13" fill="#16a34a">a</text>'
            '</svg>'
        )

    def _svg_angle(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="250" viewBox="0 0 300 250">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Two rays
            '<line x1="50" y1="200" x2="270" y2="200" stroke="#2563eb" stroke-width="2.5"/>'
            '<line x1="50" y1="200" x2="180" y2="50" stroke="#2563eb" stroke-width="2.5"/>'
            # Arc for angle
            '<path d="M 100,200 A 50,50 0 0,1 82,170" fill="none" stroke="#dc2626" stroke-width="2"/>'
            # Angle label
            '<text x="105" y="185" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626">θ</text>'
            # Vertex
            '<circle cx="50" cy="200" r="4" fill="#dc2626"/>'
            '<text x="35" y="220" font-family="Arial" font-size="13" font-weight="bold" fill="#334155">O</text>'
            '</svg>'
        )

    def _svg_trig_triangle(self, desc: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="380" height="320" viewBox="0 0 380 320">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            # Right triangle
            '<polygon points="60,260 300,260 60,80" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>'
            # Right angle marker
            '<polyline points="60,230 90,230 90,260" fill="none" stroke="#dc2626" stroke-width="1.5"/>'
            # Angle theta at base
            '<path d="M 250,260 A 50,50 0 0,1 268,230" fill="none" stroke="#f59e0b" stroke-width="2"/>'
            '<text x="240" y="245" font-family="Arial" font-size="16" font-weight="bold" fill="#f59e0b">θ</text>'
            # Labels
            '<text x="35" y="175" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#dc2626" transform="rotate(-90 35 175)">Opposite (P)</text>'
            '<text x="180" y="285" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#16a34a">Adjacent (B)</text>'
            '<text x="200" y="155" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#2563eb" transform="rotate(-37 200 155)">Hypotenuse (H)</text>'
            # Vertices
            '<text x="45" y="275" font-family="Arial" font-size="13" font-weight="bold" fill="#334155">A</text>'
            '<text x="305" y="275" font-family="Arial" font-size="13" font-weight="bold" fill="#334155">B</text>'
            '<text x="45" y="75" font-family="Arial" font-size="13" font-weight="bold" fill="#334155">C</text>'
            # Formulas box
            '<rect x="60" y="5" width="260" height="65" rx="6" fill="#dbeafe"/>'
            '<text x="190" y="25" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#1e40af">sin θ = Opposite / Hypotenuse = P/H</text>'
            '<text x="190" y="43" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#1e40af">cos θ = Adjacent / Hypotenuse = B/H</text>'
            '<text x="190" y="61" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#1e40af">tan θ = Opposite / Adjacent = P/B</text>'
            '</svg>'
        )

    def _svg_fallback(self, desc: str) -> str:
        """Fallback diagram with description text, nicely styled."""
        lines = []
        words = desc.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > 45:
                lines.append(current_line)
                current_line = word
            else:
                current_line = f"{current_line} {word}".strip()
        if current_line:
            lines.append(current_line)
        lines = lines[:5]  # Max 5 lines

        text_elements = "".join(
            f'<text x="175" y="{100 + i * 22}" text-anchor="middle" font-family="Arial" font-size="13" fill="#334155">{self._escape_svg(line)}</text>'
            for i, line in enumerate(lines)
        )

        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="350" height="250" viewBox="0 0 350 250">'
            '<rect width="100%" height="100%" fill="#f8f9fa" rx="8"/>'
            '<rect x="10" y="10" width="330" height="230" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" rx="6"/>'
            '<rect x="60" y="20" width="230" height="30" rx="6" fill="#e0f2fe"/>'
            '<text x="175" y="42" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#0369a1">Diagram</text>'
            f'{text_elements}'
            '</svg>'
        )

    def _escape_svg(self, value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;")
        )
