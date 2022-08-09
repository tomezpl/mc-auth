import React from 'react';
import ReactDOM from 'react-dom';
import { Container, Row, Col, Accordion, Badge } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles.css';

// Setup React.
const domContainer = document.getElementById('main');
const root = ReactDOM.createRoot(domContainer);

root.render(
    <Container className="shadow vh-100" id="main-container">
        <Row id="header">
            <Col xs={2} />
            <Col xs={8}>
                <h1 id="header-text" class="p-2 text-center minecraft-font text-light">DigiHub Minecraft Whitelister</h1>
            </Col>
            <Col xs={2} />
        </Row>
        <Row id="body">
            <Col xs={0} md={2} lg={3}></Col>
            <Col xs={12} md={8} lg={6}>
                <h2>How do I join?</h2>
                <p>The Minecraft server currently operates a whitelist in order to allow people access.</p>
                <p>The purpose of the whitelist is to prevent random players from joining; it's a private server intended to be used by our Discord only.</p>
                <p><strong>If you don't yet have access to the Minecraft server,</strong> and you wish to play, you must:</p>
                <Col xs={3} />
                <Col lg={12}>
                    <Accordion className="mb-3 guide-accordion">
                        <Accordion.Item eventKey="0">
                            <Accordion.Header>
                                Be part of the DigiHub Discord server.
                            </Accordion.Header>
                            <Accordion.Body>
                                We cannot provide an invite link here, as this is often abused and links end up being shared to strangers without notice.
                            </Accordion.Body>
                        </Accordion.Item>
                        <Accordion.Item eventKey="1">
                            <Accordion.Header>
                                Have the 'Minecraft' role in the DigiHub Discord server.
                            </Accordion.Header>
                            <Accordion.Body>
                                <p>
                                    You can do this yourself by assigning the Minecraft role as per the <Badge className="align-middle" bg="secondary">
                                        <span class="fs-5 fw-light fst-italic"># </span>
                                        <span class="align-text-top">self-roles</span>
                                    </Badge> text channel.
                                </p>
                                <p>
                                    <strong>If you need any help,</strong> feel free to contact the Discord admins or send a message in the <Badge className="align-middle" bg="secondary">
                                        <span class="fs-5 fw-light fst-italic"># </span>
                                        <span class="align-text-top">minecraft</span>
                                    </Badge> text channel.
                                </p>
                                <p>
                                    <small class="fst-italic text-secondary">It's almost inevitable something will go wrong and Tom will need to fix it... ugh.</small>
                                </p>
                            </Accordion.Body>
                        </Accordion.Item>
                        <Accordion.Item eventKey="2">
                            <Accordion.Header>
                                Use the authenticator tool on this Web page with your Discord account
                            </Accordion.Header>
                            <Accordion.Body>
                                <p>The tool, which you can find by scrolling further down on this Web page, will ask you to sign-in to your Discord account.</p>
                                <p>Your password and personal details remain safe, as everything is carried out via Discord's official API.</p>
                                <p>Upon sign-in, the tool will verify your membership and roles. If you meet the criteria listed above, you will be asked to enter your Minecraft player name, and you will be immediately whitelisted on the server.</p>
                            </Accordion.Body>
                        </Accordion.Item>
                    </Accordion>
                </Col>
                <Col xs={3} />
            </Col>
            <Col xs={0} md={2} lg={3}></Col>
            <Col xs={1} />
            <Col xs={10}>
                <hr />
            </Col>
            <Col xs={1} />

            <Col xs={12}>
                <a href="/signin">
                    Click here!
                </a>
            </Col>
        </Row>
        <Row id="footer">

        </Row>
    </Container>
);