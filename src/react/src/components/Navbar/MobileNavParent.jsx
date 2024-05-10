import React from 'react';

import MobileNavSubmenuColumnSection from './MobileNavSubmenuColumnSection';
import { BackButtonArrowLeft, MobileSubmenuButtonArrowRight } from './navIcons';

export default function MobileNavParent({
    label,
    columns,
    isActive,
    setActive,
    setInactive,
}) {
    return (
        <>
            <button
                type="button"
                className="mobile-nav-submenu-button"
                onClick={setActive}
            >
                <span>{label}</span>
                <MobileSubmenuButtonArrowRight />
            </button>

            <div
                className="mobile-nav-submenu"
                style={
                    isActive
                        ? { width: '100%', height: 'auto', left: '100%' }
                        : {}
                }
            >
                <button
                    type="button"
                    className="mobile-nav-back-button"
                    onClick={setInactive}
                >
                    <BackButtonArrowLeft />
                    <span>Back</span>
                </button>

                {columns.flat().map((columnSection, index) => (
                    <MobileNavSubmenuColumnSection
                        key={columnSection.label}
                        columnSection={columnSection}
                        startOpen={index === 0}
                    />
                ))}
            </div>
        </>
    );
}
