import React from 'react';

/*
Whether data points are drawn plainly: the label and value only, without
who contributed it, when, or how many sources agree. An embedded map shows a
location that way, since it only ever carries its own contributor's data.
*/
const PlainDataPointContext = React.createContext(false);

export default PlainDataPointContext;
