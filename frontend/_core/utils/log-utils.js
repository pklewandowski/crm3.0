import {SystemException} from "../exception";

class LogUtils {
    static log(msg, stack, raiseError=false){
        //todo: finally log to server via Ajax call
        console.log(msg, stack);
        if (raiseError){
            throw new SystemException(msg);
        }
    }
}

export default LogUtils;