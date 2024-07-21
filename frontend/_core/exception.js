class BaseException{
    constructor(message) {
        this.message = message;
        this.name = 'BaseException';
    }
}
class SystemException extends BaseException{
    constructor(message) {
        super(message);
        this.name = 'SystemException';
    }
}

class NotImplementedException extends BaseException {
    constructor(message) {
        super(message);
        if(!message) {
            message = 'Function not implemented';
        }
        this.name = 'NoImplementedException';
    }
}

export {SystemException, NotImplementedException}