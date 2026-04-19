import React from 'react';

const styles = Object.freeze({
    container: Object.freeze({
        padding: '24px 0',
    }),
    title: Object.freeze({
        fontWeight: '900',
        fontSize: '24px',
        lineHeight: '28px',
        margin: '0 0 16px 0',
    }),
});

function UserProfileFacilities() {
    return (
        <div style={styles.container}>
            <h3 style={styles.title}>Facilities</h3>
        </div>
    );
}

export default UserProfileFacilities;
