class GraphUtils {

    desaturate(r, g, b) {
        var intensity = 0.3 * r + 0.59 * g + 0.11 * b;
        var k = 1;
        r = Math.floor(intensity * k + r * (1 - k));
        g = Math.floor(intensity * k + g * (1 - k));
        b = Math.floor(intensity * k + b * (1 - k));
        return [r, g, b];
    }


    /**
     color - hex value
     saturation - [0:100]
     */
    desaturateColor(color, saturation) {
        let col = hexToRgb(color);
        let sat = Number(saturation) / 100;
        let gray = col.r * 0.3086 + col.g * 0.6094 + col.b * 0.0820;

        col.r = Math.round(col.r * sat + gray * (1 - sat));
        col.g = Math.round(col.g * sat + gray * (1 - sat));
        col.b = Math.round(col.b * sat + gray * (1 - sat));

        var out = rgbToHex(col.r, col.g, col.b);

        $('#output').val(out);

        $('body').css("background", out);
    }

    componentToHex(c) {
        var hex = c.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
    }

    rgbToHex(r, g, b) {
        return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
    }

    hexToRgb(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
}

export default GraphUtils;

