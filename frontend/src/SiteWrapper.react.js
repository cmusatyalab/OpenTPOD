import React from "react";
import { NavLink, withRouter } from "react-router-dom";
import { Site, Nav, Button, RouterContextProvider } from "tabler-react";
import { endpoints } from "./const";
import { uiAuth } from "./util.js";

const navBarItems = [
    {
        value: "Video",
        to: endpoints.uiVideo,
        icon: "home",
        LinkComponent: withRouter(NavLink),
        useExact: true
    },
    {
        value: "Detector",
        to: endpoints.uiDetector,
        icon: "code",
        LinkComponent: withRouter(NavLink)
    },
    {
        value: "Load Data",
        to: endpoints.uiLoadData,
        icon: "code",
        LinkComponent: withRouter(NavLink),
        useExact: true
    },
    {
        value: "Load Model",
        // to: endpoints.detectormodels,
        to: endpoints.uiLoadModel,
        icon: "code",
        LinkComponent: withRouter(NavLink),
        useExact: true
    }
];

class SiteWrapper extends React.Component {
    render() {
        return (
            <Site.Wrapper
                headerProps={{
                    href: "/",
                    alt: "TPOD",
                    imageURL: "/static/tpod-logo.png",
                    navItems: (
                        <Nav.Item type="div" className="d-none d-md-flex">
                            <Button
                                outline
                                size="sm"
                                RootComponent="button"
                                color="primary"
                                onClick={() => {
                                    uiAuth.logout().then(() => {
                                        this.props.history.push(
                                            endpoints.uiHome
                                        );
                                    });
                                }}
                            >
                                Log Out
                            </Button>
                        </Nav.Item>
                    )
                }}
                navProps={{ itemsObjects: navBarItems }}
                routerContextComponentType={withRouter(RouterContextProvider)}
                footerProps={{
                    links: [],
                    note: "Tools for Painless Object Detection.",
                    copyright: (
                        <React.Fragment>
                            Copyright © 2019
                            <a href="http://gabriel.cs.cmu.edu">
                                {" "}
                                Carnegie Mellon University
                            </a>
                            . UI theme powered by
                            <a
                                href="https://github.com/tabler/tabler-react"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {" "}
                                Tabler-React
                            </a>{" "}
                            All rights reserved.
                        </React.Fragment>
                    )
                }}
            >
                {this.props.children}
            </Site.Wrapper>
        );
    }
}

export default withRouter(SiteWrapper);
