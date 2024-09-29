class IdUtils {
    static guid() {
        return IdUtils.s4() + IdUtils.s4() + '-' + IdUtils.s4() + '-' + IdUtils.s4() + '-' +
            IdUtils.s4() + '-' + IdUtils.s4() + IdUtils.s4() + IdUtils.s4();
    }

    static s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
}

export default IdUtils;