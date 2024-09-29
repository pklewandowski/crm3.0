class HtmlUtils {

    static escapeScriptTag(str) {
        return str.replace(new RegExp("<script>|</script>", 'g'), '');
    }
}

export default HtmlUtils;