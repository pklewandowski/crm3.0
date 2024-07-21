class Avatar {
    /**
     *
     * @param avatarFileName - name of the avatar file
     * @param userName - must be dictionary {firstName: FIRST_NAME|null, lastName:LAST_NAME|null}
     */
    constructor(avatarFileName = null, userName = null) {
        this.avatarFilename = avatarFileName;
        this.userName = userName;
        this.initials = `${userName.lastName?userName.lastName[0]:''}${userName.firstName?userName.firstName[0]:''}`;
    }

    render() {
        if (!this.avatarFilename && !this.initials) {
            return jsUtils.Utils.domElement('div');
        }
        if (this.avatarFilename) {
            let img = jsUtils.Utils.domElement('img');
            img.src = `/media/avatar/${this.avatarFilename}`;
            return img;
        } else {
            let initials = jsUtils.Utils.domElement('div', '', 'avatar-initials');
            initials.innerText = this.initials;
            return initials;
        }
    }
}

export {Avatar};