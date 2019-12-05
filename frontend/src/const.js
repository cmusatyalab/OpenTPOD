const endpoints = {
    login: "/auth/login/",
    logout: "/auth/logout/",
    user: "/auth/user/",
    registration: "/auth/registration/",
    tasks: "/api/v1/tasks",
    detectors: "/api/opentpod/v1/detectors",
    detectorDnnTypes: "/api/opentpod/v1/detectors/types",
    dnnTrainingConfigs: "/api/opentpod/v1/detectors/training_configs",
    tensorboard: "/api/opentpod/tensorboard/index.html",
    detectorDownloadField: "model",
    detectorVisualizationField: "visualization",
    trainsets: "/api/opentpod/v1/trainsets",
    mediaData: "/media/data/",
    // front end handled routes
    uiVideo: "/video",
    uiLabel: "/label", // TODO (junjuew): still need this?
    uiAnnotate: "/annotate",
    uiDetector: "/detector",
    uiDetectorNew: "/detector-new"
};

// this value should be the same as 'PAGE_SIZE' in backend
// django settings
const PAGE_SIZE = 2;

// Style Select to fit into site's theme
const reactSelectTablerStyles = {
    control: (provided, state) => ({
        ...provided,
        border: "1px solid rgba(0, 40, 100, 0.12)",
        borderRadius: "3px"
    }),
    placeholder: (provided, state) => ({
        ...provided,
        opacity: "0.6"
    })
};

export { endpoints, PAGE_SIZE, reactSelectTablerStyles };
