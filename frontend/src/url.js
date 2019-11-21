const endpoints = {
    login: "/auth/login/",
    logout: "/auth/logout/",
    user: "/auth/user/",
    registration: "/auth/registration/",
    tasks: "/api/v1/tasks",
    detectors: "/api/opentpod/v1/detectors",
    media: "/media/",
    mediaData: "/media/data/",
    // front end handled routes
    video: "/video",
    label: "/label", // TODO (junjuew): still need this?
    annotate: "/annotate",
    detector: "/detector"
};
export { endpoints };
