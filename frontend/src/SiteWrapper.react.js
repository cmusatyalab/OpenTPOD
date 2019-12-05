import * as React from "react";
import { NavLink, withRouter } from "react-router-dom";
import { endpoints } from "./const";

import {
    Site,
    Nav,
    Grid,
    List,
    Button,
    RouterContextProvider
} from "tabler-react";

const navBarItems = [
    {
        value: "Video",
        to: endpoints.uiVideo,
        icon: "home",
        LinkComponent: withRouter(NavLink),
        useExact: true
    },
    // {
    //     value: "Label",
    //     to: endpoints.uiLabel,
    //     icon: "edit",
    //     LinkComponent: withRouter(NavLink)
    // },
    {
        value: "Detector",
        to: endpoints.uiDetector,
        icon: "code",
        LinkComponent: withRouter(NavLink)
    }
];

const accountDropdownProps = {
    // avatarURL: "./demo/faces/female/25.jpg",
    name: "Admin",
    description: "Administrator",
    options: [
        { icon: "user", value: "Profile" },
        { icon: "settings", value: "Settings" },
        { icon: "mail", value: "Inbox", badge: "6" },
        { icon: "send", value: "Message" },
        { isDivider: true },
        { icon: "help-circle", value: "Need help?" },
        { icon: "log-out", value: "Sign out" }
    ]
};

class SiteWrapper extends React.Component {
    state = {
        notificationsObjects: [
            {
                unread: false,
                avatarURL: "demo/faces/female/18.jpg",
                message: (
                    <React.Fragment>
                        <strong>Rose</strong> deployed new version of NodeJS
                        REST Api // V3
                    </React.Fragment>
                ),
                time: "2 hours ago"
            }
        ]
    };

    render() {
        const notificationsObjects = this.state.notificationsObjects || [];
        const unreadCount = this.state.notificationsObjects.reduce(
            (a, v) => a || v.unread,
            false
        );
        return (
            <Site.Wrapper
                headerProps={{
                    href: "/",
                    alt: "TPOD",
                    imageURL: "tpod-logo.png",
                    navItems: (
                        <Nav.Item type="div" className="d-none d-md-flex">
                            <Button
                                href="https://github.com/cmusatyalab/tpod"
                                target="_blank"
                                outline
                                size="sm"
                                RootComponent="a"
                                color="primary"
                            >
                                Source code
                            </Button>
                        </Nav.Item>
                    ),
                    notificationsTray: {
                        notificationsObjects,
                        markAllAsRead: () =>
                            this.setState(
                                () => ({
                                    notificationsObjects: this.state.notificationsObjects.map(
                                        v => ({ ...v, unread: false })
                                    )
                                }),
                                () =>
                                    setTimeout(
                                        () =>
                                            this.setState({
                                                notificationsObjects: this.state.notificationsObjects.map(
                                                    v => ({
                                                        ...v,
                                                        unread: true
                                                    })
                                                )
                                            }),
                                        5000
                                    )
                            ),
                        unread: unreadCount
                    },
                    accountDropdown: accountDropdownProps
                }}
                navProps={{ itemsObjects: navBarItems }}
                routerContextComponentType={withRouter(RouterContextProvider)}
                footerProps={{
                    links: [
                        <a href="#">First Link</a>,
                        <a href="#">Second Link</a>,
                        <a href="#">Third Link</a>,
                        <a href="#">Fourth Link</a>,
                        <a href="#">Five Link</a>,
                        <a href="#">Sixth Link</a>,
                        <a href="#">Seventh Link</a>,
                        <a href="#">Eigth Link</a>
                    ],
                    note:
                        "Premium and Open Source dashboard template with responsive and high quality UI. For Free!",
                    copyright: (
                        <React.Fragment>
                            Copyright © 2019
                            <a href="."> Tabler-react</a>. Theme by
                            <a
                                href="https://codecalm.net"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {" "}
                                codecalm.net
                            </a>{" "}
                            All rights reserved.
                        </React.Fragment>
                    ),
                    nav: (
                        <React.Fragment>
                            <Grid.Col auto={true}>
                                <List className="list-inline list-inline-dots mb-0">
                                    <List.Item className="list-inline-item">
                                        <a href="./docs/index.html">
                                            Documentation
                                        </a>
                                    </List.Item>
                                    <List.Item className="list-inline-item">
                                        <a href="./faq.html">FAQ</a>
                                    </List.Item>
                                </List>
                            </Grid.Col>
                            <Grid.Col auto={true}>
                                <Button
                                    href="https://github.com/tabler/tabler-react"
                                    size="sm"
                                    outline
                                    color="primary"
                                    RootComponent="a"
                                >
                                    Source code
                                </Button>
                            </Grid.Col>
                        </React.Fragment>
                    )
                }}
            >
                {this.props.children}
            </Site.Wrapper>
        );
    }
}

export default SiteWrapper;
