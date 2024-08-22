import React from 'react';
import ReactDOM from 'react-dom';

function App() {
    const [message, setMessage] = React.useState("Hello, Flask with React!");

    return (
        <div>
            <h1>{message}</h1>
            <button onClick={() => setMessage("Button Clicked!")}>Click Me</button>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
