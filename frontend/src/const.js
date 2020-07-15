const endpoints = {
    login: "/auth/login/",
    logout: "/auth/logout/",
    user: "/auth/user/",
    registeration: "/auth/registration/",
    tasks: "/api/v1/tasks",
    detectors: "/api/opentpod/v1/detectors",
    detectorDnnTypes: "/api/opentpod/v1/detectors/types",
    dnnTrainingConfigs: "/api/opentpod/v1/detectors/training_configs",
    userInfo: "/api/v1/users/self",
    detectorDownloadField: "model",
    detectorVisualizationField: "visualization/index.html",
    trainsets: "/api/opentpod/v1/trainsets",
    detectormodels: "/api/opentpod/v1/detectormodels",
    mediaData: "/task_data/",
    fileLoad: "/media/TrainModel",
    logo: "/static/tpod-logo.png",
    // front end handled routes
    uiSignup: "/signup",
    uiLogin: "/login",
    uiVideo: "/video",
    uiLabel: "/label",
    uiAnnotate: "/annotate",
    uiDetector: "/detector",
    uiDetectorNew: "/detector-new",
    uiLoadData:"/load-data",
    uiLoadModel:"/load-model",
    uiModelNew:"/load-model-new",
    uiHome: "/"
};

const session_storage_key = {
    userId: "userId",
    isAuthenticated: "isAuthenticated"
};

// this value should be the same as 'PAGE_SIZE' in backend
// django settings
const PAGE_SIZE = 10;

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

export { endpoints, PAGE_SIZE, reactSelectTablerStyles, session_storage_key };
