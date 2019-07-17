
import * as React from "react";
import { Alert } from "tabler-react";
function logFetchErrors(response) {
    if (!response.ok) {
        console.error(response);
    }
    throw response;
}

function fetchJSON(url, method, data = {}) {
    method = method.toUpperCase();
    let options = {
        method: method,
        credentials: 'include', // make sure cookies are sent
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    };
    if (method === 'GET' || method === 'HEAD') {
        delete options.body;
    }

    return fetch(url, options)
        .then(logFetchErrors)
        .then(response => response.json());
}

function checkAuth() {
    fetchJSON('/session/authenticated', 'GET')
        .then(resp => {
            return true;
        }).catch(
            e => false
        );
}

function withFormikStatus(component, status) {
    return <>
        {
            status &&
            <Alert type='danger'>
                {status}
            </Alert>
        }
        {component}
    </>
}

export { checkAuth, fetchJSON, withFormikStatus }