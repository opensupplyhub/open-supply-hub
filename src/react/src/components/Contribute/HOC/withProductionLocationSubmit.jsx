import React from 'react';
import { useParams } from 'react-router-dom';

const withProductionLocationSubmit = WrappedComponent => props => {
    const { osID } = useParams();
    const submitMethod = osID ? 'PATCH' : 'POST';

    return <WrappedComponent {...props} submitMethod={submitMethod} />;
};

export default withProductionLocationSubmit;
