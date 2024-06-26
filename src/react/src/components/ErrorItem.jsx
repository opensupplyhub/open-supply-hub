import React from 'react';

const ErrorItem = ({ errorText }) => {
    const parser = new DOMParser();
    const parsedString = parser
        .parseFromString(errorText, 'text/html')
        .querySelector('body').innerHTML;

    function createMarkup() {
        return {
            __html: parsedString,
        };
    }

    return (
        <li
            key={errorText}
            style={{ color: 'red' }}
            className="content"
            dangerouslySetInnerHTML={createMarkup()}
        />
    );
};

export default ErrorItem;
