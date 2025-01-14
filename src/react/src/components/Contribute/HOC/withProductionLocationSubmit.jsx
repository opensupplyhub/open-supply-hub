import React from 'react';
import { useParams } from 'react-router-dom';

const withProductionLocationSubmit = WrappedComponent => () => {
    const { osID } = useParams();
    const submitMethod = osID ? 'PATCH' : 'POST';

    return <WrappedComponent submitMethod={submitMethod} />;
};

export default withProductionLocationSubmit;
