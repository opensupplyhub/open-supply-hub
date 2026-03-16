import React from 'react';

const MapPointer = props => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width={props.width || '24'}
        height={props.height || '24'}
        viewBox={props.viewBox || '0 0 24 24'}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="lucide lucide-map-pin w-4 h-4"
        {...props}
    >
        <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" />
        <circle cx="12" cy="10" r="3" />
    </svg>
);

export default MapPointer;
