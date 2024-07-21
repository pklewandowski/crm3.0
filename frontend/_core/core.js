function isSaved(errMsg='Proszę zapisać zmiany') {
    if (_g && _g.hasOwnProperty('saved') && !_g.saved) {
        window.Alert.warning(errMsg);
        return false;
    }
    return true;
}

export {isSaved};