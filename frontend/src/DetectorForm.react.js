import React, { useState, useEffect } from "react";
import { useHistory, useParams } from "react-router-dom";
import { Formik } from "formik";
import URI from "urijs";
import {
    Button,
    Card,
    Dimmer,
    Grid,
    Page,
    List,
    Form,
    FormTextInput,
    FormCard
} from "tabler-react";
import SiteWrapper from "./SiteWrapper.react";
import { endpoints } from "./url";
import { fetchJSON, lineWrap, downloadByPoll as checkDownload } from "./util";
import defaultStrings from "./DetectorPage.strings";
import { TrainSetNewForm } from "./TrainSetPage.react";
import "./App.css";

const fetchTasks = async page => {
    let url = new URI(endpoints.tasks);
    url.addSearch("page", page);
    return await fetchJSON(url.toString(), "GET");
};

const filterTasksByName = async searchString => {
    let url = new URI(endpoints.tasks);
    url.addSearch("name", searchString);
    return await fetchJSON(url.toString(), "GET");
};

const loadAndSearchTasks = async (search, options, { page }) => {
    let filteredOptions;
    let hasMore;
    let curTasks;
    let curOptions;
    let nextPage;
    if (!search) {
        curTasks = await fetchTasks(page);
        curOptions = curTasks.results.map(task => {
            return {
                value: task.id,
                label: `${task.id} + ${task.name}`
            };
        });
        // backend's returned count is the total # of entries
        hasMore = curTasks.count > options.length + curOptions.length;
        nextPage = page + 1;
    } else {
        curTasks = await filterTasksByName(search.toLowerCase());
        curOptions = curTasks.results.map(task => {
            return {
                value: task.id,
                label: `${task.id} + ${task.name}`
            };
        });
        hasMore = false;
        nextPage = page;
    }
    filteredOptions = curOptions;
    return {
        options: filteredOptions,
        hasMore: hasMore,
        additional: {
            page: nextPage
        }
    };
};

export { loadAndSearchTasks };
