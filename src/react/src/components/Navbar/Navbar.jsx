import React, { useEffect, useState } from 'react';

import useNavbarRenderer from './useNavbarRenderer';
import '../../styles/css/header.scss';
import { MobileNavbarItems, NavbarItems } from '../../util/constants';
import Logo from './Logo';
import BurgerButton from './BurgerButton';
import NavbarQ42022Banner from './NavbarQ42022Banner';
import MenuClickHandlerContext from './MenuClickHandlerContext';

const breakpoint = '(max-width: 75rem)';

export default function Navbar() {
    const [mobileMode, setMobileMode] = useState(
        window.matchMedia(breakpoint).matches,
    );

    const [showMobileMenu, setShowMobileMenu] = useState(false);

    useEffect(() => {
        const handleMediaChange = e => setMobileMode(e.matches);
        const mediaQueryList = window.matchMedia(breakpoint);

        if (typeof mediaQueryList.addEventListener === 'function') {
            mediaQueryList.addEventListener('change', handleMediaChange);
        } else {
            mediaQueryList.addListener(handleMediaChange);
        }

        return () => {
            if (typeof mediaQueryList.addEventListener === 'function') {
                mediaQueryList.removeEventListener('change', handleMediaChange);
            } else {
                mediaQueryList.removeListener(handleMediaChange);
            }
        };
    }, []);

    const [activeSubmenu, setActiveSubmenu] = useState(null);

    useEffect(() => {
        if (mobileMode) {
            // Don't automatically open submenu on entering mobile mode
            // because the mobile menu is not automatically open
            setActiveSubmenu(null);
        } else {
            // Reset mobile menu on entering desktop mode,
            // but preserve active submenu
            setShowMobileMenu(false);
        }
    }, [mobileMode]);

    useEffect(() => {
        if (activeSubmenu) {
            const closeHeaderOnOutsideClick = event => {
                const headerElement = document.getElementById('header');
                const headerWasClicked = headerElement.contains(event.target);

                if (!headerWasClicked) {
                    setActiveSubmenu(null);
                }
            };

            document.addEventListener('click', closeHeaderOnOutsideClick);

            return () => {
                document.removeEventListener(
                    'click',
                    closeHeaderOnOutsideClick,
                );
            };
        }

        return () => {};
    }, [activeSubmenu]);

    const {
        renderNavItem,
        renderMobileNavItem,
        getMobileNavItemClass,
    } = useNavbarRenderer({
        activeSubmenu,
        setActiveSubmenu,
    });

    const headerClassName = `header header-height-contributor ${
        mobileMode ? ' mobile-nav-is-active' : ''
    }`;

    // TODO: The local development error has been temporarily suppressed
    //       with the ternary operator. The proper fix will be
    //       implemented within the OSDEV-756 bug ticket.
    const isStaging = window.ENVIRONMENT
        ? window.ENVIRONMENT.ENVIRONMENT === 'staging'
        : false;

    const Header = (
        <header className={headerClassName} id="header">
            <div
                className={`header__main${
                    isStaging ? ' header__main--staging' : ''
                }`}
            >
                <Logo />
                <nav className="nav" id="nav" role="navigation">
                    {NavbarItems.map(item => {
                        const key = item.label ?? item.type;
                        return (
                            <div
                                key={key}
                                className={`nav-item${
                                    activeSubmenu === key
                                        ? ' nav-submenu-is-active'
                                        : ''
                                }`}
                            >
                                {renderNavItem(item)}
                            </div>
                        );
                    })}
                </nav>

                {showMobileMenu ? (
                    <nav
                        className="mobile-nav"
                        id="mobile-nav"
                        role="navigation"
                        style={!activeSubmenu ? { opacity: 1, left: '0%' } : {}}
                    >
                        <div className="mobile-nav__main">
                            {MobileNavbarItems.map((item, index) => (
                                <div
                                    key={item.label || item.type}
                                    className={getMobileNavItemClass(
                                        item,
                                        index === MobileNavbarItems.length - 1,
                                    )}
                                >
                                    {renderMobileNavItem(item)}
                                </div>
                            ))}
                        </div>
                    </nav>
                ) : null}

                <BurgerButton
                    showMobileMenu={showMobileMenu}
                    toggleMobileMenu={() => setShowMobileMenu(open => !open)}
                />
            </div>
        </header>
    );

    const createMenuClickHandler = (callback = () => {}) => () => {
        setActiveSubmenu(null);
        setShowMobileMenu(false);
        callback();
    };

    return (
        <>
            <NavbarQ42022Banner />
            <MenuClickHandlerContext.Provider value={createMenuClickHandler}>
                {Header}
            </MenuClickHandlerContext.Provider>
        </>
    );
}
