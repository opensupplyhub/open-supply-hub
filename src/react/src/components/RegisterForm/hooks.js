import { useState, useEffect, useRef } from 'react';

const useRegistrationFormSubmit = (fetching, error, clearForm) => {
    const [formSubmitted, setFormSubmitted] = useState(false);
    const prevFetchingRef = useRef(fetching);

    useEffect(() => {
        const wasFetching = prevFetchingRef.current;
        prevFetchingRef.current = fetching;

        if (!error && !fetching && wasFetching) {
            setFormSubmitted(true);
        }
    });

    useEffect(() => () => clearForm(), [clearForm]);

    return formSubmitted;
};

export default useRegistrationFormSubmit;
