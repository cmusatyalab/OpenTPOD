import * as React from "react";
import { Alert } from "tabler-react";
import { endpoints } from "./url";

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

export {
    checkAuth,
    fetchJSON,
    checkDownload as downloadByPoll,
    withFormikStatus,
    lineWrap
};
