
import * as React from "react";
import { Alert } from "tabler-react";
import { endpoints } from "./url"


function logFetchErrors(response) {
    if (!response.ok) {
        console.error(response);
        throw response;
    }
    return response
}

function fetchJSON(url, method, data = {}) {
    method = method.toUpperCase();
    let options = {
        method: method,
        credentials: 'include', // make sure cookies are sent
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data),
    };
    if (method === 'GET' || method === 'HEAD') {
        delete options.body;
    }

    return fetch(url, options)
        .then(response => logFetchErrors(response))
        .then(response => {
            return response.text().then(text => {
                return text ? JSON.parse(text) : {}
            });
        })
};

function checkAuth() {
    fetchJSON(endpoints.user, 'GET')
        .then(resp => true).catch(e => false);
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
