import React from 'react';
import ReactDOM from 'react-dom';
import { Container, Row, Col, Accordion, Badge, Form, FormControl, Button, Modal } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles.css';

// Setup React.
const domContainer = document.getElementById('main');
const root = ReactDOM.createRoot(domContainer);

function getUserInfo() {
    return new Promise((resolve, reject) => {
        fetch('/userinfo', { method: 'GET' })
            .then((response) => {
                response.json().then((data) => {
                    if (data != null && data != undefined && Object.keys(data) !== 0) {
                        resolve({
                            userName: data.userName
                        });
                    }
                    else {
                        resolve({
                            userName: null
                        });
                    }
                });
            })
            .catch((reason) => {
                reject(reason);
            });
    });
}

function getUserGameConfig() {
    return new Promise((resolve, reject) => {
        fetch('/gameconfig', { method: 'GET' })
            .then((response) => {
                response.json().then((data) => {
                    if (data != null && data != undefined && Object.keys(data) !== 0) {
                        resolve({
                            minecraftPlayerName: data.minecraftPlayerName
                        });
                    }
                    else {
                        resolve({
                            minecraftPlayerName: null
                        });
                    }
                })
            })
            .catch((reason) => {
                reject(reason);
            });
    });
}

class UpdateNameForm extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            playerName: props.playerName,
            showModal: false,
            isUpdating: false
        };
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value });
    };

    submitChange = () => {
        this.setState({showModal: true, isUpdating: true});
        fetch('/gameconfig', {method: 'PUT', body: JSON.stringify({minecraftPlayerName: this.state.playerName}), headers: {'Content-Type': 'application/json'}})
        .then((response) => {
            if(![200, 201].includes(response.status)) {
                throw 'Failed to update whitelist.';
            }
        })
        .catch((err) => {
            console.error(err);
            this.setState({playerName: this.props.playerName});
        })
        .finally(() => {
            this.setState({isUpdating: false});
        });
    }

    render() {
        let modalHeader;
        let modalBodyText;
        let modalButtons;

        if(this.state.isUpdating) {
            modalHeader = 'Please wait...';
            modalBodyText = 'Your name is currently being added to the whitelist.';
        }
        else {
            modalHeader = 'Name updated!';
            modalBodyText = 'Your name has been successfully added to the whitelist. You should now be able to connect to the server.';
            modalButtons = (<Button variant="success" onClick={() => this.setState({showModal: false})}>Close</Button>);
        }

        return (<>
            <Form>
                <Form.Group>
                    <Form.Label>Minecraft player name</Form.Label>
                    <FormControl name="playerName" onChange={this.handleChange} defaultValue={this.props.playerName} />
                    <Button variant="primary" onClick={this.submitChange}>Update</Button>
                </Form.Group>
            </Form>
            <Modal show={this.state.showModal}>

                <Modal.Header>
                    {modalHeader}
                </Modal.Header>
                <Modal.Body>
                    {modalBodyText}
                </Modal.Body>
                <Modal.Footer>
                    {modalButtons}
                </Modal.Footer>
            </Modal>
        </>);
    }
}

class MinecraftWhitelisterComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            userInfo: {
                userName: null
            },
            gameConfig: {
                minecraftPlayerName: null
            }
        };
    }

    componentDidMount() {
        getUserInfo()
            .then((userInfo) => {
                this.setState({ userInfo });
            })
            .catch(() => {
                console.error('Failed to get user info.');
                this.setState({
                    userInfo: {
                        userName: null
                    }
                });
            });

        getUserGameConfig()
            .then((gameConfig) => {
                this.setState({ gameConfig });
            })
            .catch(() => {
                console.error('Failed to get game config for user.')
                this.setState({
                    gameConfig: {
                        minecraftPlayerName: null
                    }
                });
            });
    }

    render() {
        let userInfoText;
        let signInButton;
        let updateNameForm;
        if (this.state.userInfo.userName != null) {
            userInfoText = <p>Hi {this.state.userInfo.userName}!</p>;
            updateNameForm = <UpdateNameForm playerName={this.state.gameConfig.minecraftPlayerName} />
        }
        else {
            signInButton = <a href="/signin">Click here!</a>
        }

        return (<Container className="shadow vh-100" id="main-container">
            <Row id="header">
                <Col xs={2} />
                <Col xs={8}>
                    <h1 id="header-text" className="p-2 text-center minecraft-font text-light">DigiHub Minecraft Whitelister</h1>
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
                                            <span className="fs-5 fw-light fst-italic"># </span>
                                            <span className="align-text-top">self-roles</span>
                                        </Badge> text channel.
                                    </p>
                                    <p>
                                        <strong>If you need any help,</strong> feel free to contact the Discord admins or send a message in the <Badge className="align-middle" bg="secondary">
                                            <span className="fs-5 fw-light fst-italic"># </span>
                                            <span className="align-text-top">minecraft</span>
                                        </Badge> text channel.
                                    </p>
                                    <p>
                                        <small className="fst-italic text-secondary">It's almost inevitable something will go wrong and Tom will need to fix it... ugh.</small>
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
                    {userInfoText}
                    {signInButton}
                    {updateNameForm}
                </Col>
            </Row>
            <Row id="footer">

            </Row>
        </Container>)
    }
}

root.render(<MinecraftWhitelisterComponent />);