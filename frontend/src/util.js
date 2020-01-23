import * as React from "react";
import { Alert } from "tabler-react";
import { endpoints } from "./const";

function logFetchErrors(response) {
    if (!response.ok) {
        console.error(response);
        throw response;
    }
    return response;
}

function fetchJSON(url, method, data = {}) {
    method = method.toUpperCase();
    let options = {
        method: method,
        credentials: "include", // make sure cookies are sent
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
        },
        body: JSON.stringify(data)
    };
    if (method === "GET" || method === "HEAD") {
        delete options.body;
    }

    return fetch(url, options)
        .then(response => logFetchErrors(response))
        .then(response => {
            return response.text().then(text => {
                return text ? JSON.parse(text) : {};
            });
        });
}

function checkDownload(url, interval, timeout, onSuccess, onFailure) {
    /* download url by polling
     * interval: the minimum interval (ms) between subsequent pollling request
     * timeout: the total time of polling. the polling will stop after timeout
     */
    let startTime = new Date();
    let curTime = null;
    let options = {
        method: "GET",
        credentials: "include" // make sure cookies are sent
    };
    const pollUrl = () => {
        fetch(url, options).then(response => {
            if (response.status === 200) {
                onSuccess(response);
            } else {
                curTime = new Date();
                if (curTime - startTime < timeout) {
                    setTimeout(pollUrl, interval);
                } else {
                    onFailure();
                }
            }
        });
    };
    pollUrl();
}

const uiAuth = {
    isAuthenticated: false,

    login(data) {
        return fetchJSON(endpoints.login, "POST", data).then(() => {
            this.isAuthenticated = true;
        });
    },

    logout() {
        this.isAuthenticated = false;
        return fetchJSON(endpoints.logout, "POST", {});
    }
};

function checkAuth() {
    fetchJSON(endpoints.user, "GET")
        .then(resp => true)
        .catch(e => false);
}

function withFormikStatus(component, status) {
    return (
        <>
            {status && <Alert type="danger">{status}</Alert>}
            {component}
        </>
    );
}

function lineWrap(input, breakAt = 10) {
    let regex = `/(.{${breakAt}})/g`;
    input.replace(regex, "$1\n");
    return input;
}

function clamp(num, min, max) {
    return num <= min ? min : num >= max ? max : num;
}
/**
 * Returns an object of fields with values set based on the touched and error values
 * If a value is both touched and has a non-empty error string it is returned as the fields value
 */
function touchedErrors(touched = {}, errors = {}, fields = []) {
    return fields.reduce(
        (acc, cur) =>
            Object.assign(acc, {
                [cur]: touched && touched[cur] && errors ? errors[cur] : ""
            }),
        {}
    );
}

/**
 * A HOC that modifies the errors propso that it only returns errors if the the field
 * has also been touched
 * First takes an array of the field names, followed by the component
 */
function withTouchedErrors(fields = []) {
    return function withComponent(Component) {
        return function WithTouchedErrors(props) {
            const errors = touchedErrors(props.touched, props.errors, fields);
            return <Component {...props} errors={errors} />;
        };
    };
}

export {
    checkAuth,
    fetchJSON,
    checkDownload as downloadByPoll,
    withFormikStatus,
    lineWrap,
    clamp,
    withTouchedErrors,
    uiAuth
};
