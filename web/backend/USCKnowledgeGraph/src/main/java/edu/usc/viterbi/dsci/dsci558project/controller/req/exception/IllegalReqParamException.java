package edu.usc.viterbi.dsci.dsci558project.controller.req.exception;

public class IllegalReqParamException extends Exception {

    public IllegalReqParamException() {
    }

    public IllegalReqParamException(String message) {
        super(message);
    }

    public IllegalReqParamException(String message, Throwable cause) {
        super(message, cause);
    }

    public IllegalReqParamException(Throwable cause) {
        super(cause);
    }

    public IllegalReqParamException(String message, Throwable cause, boolean enableSuppression, boolean writableStackTrace) {
        super(message, cause, enableSuppression, writableStackTrace);
    }

}
