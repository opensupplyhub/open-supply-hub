import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';
import DataSourceItem from './DataSourceItem';
import DataSourceDetail from './DataSourceDetail';
import {
    DATA_SOURCES_TOOLTIP_TEXT,
    DATA_SOURCES_LEARN_MORE_URL,
    DATA_SOURCES_ITEMS,
    DATA_LABELS_TITLE,
} from './constants';
import productionLocationDetailsDataSourcesInfoStyles from './styles';

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => {
    /*
    The detail slide keeps the last opened item mounted after the panel slides
    back, so the outgoing slide does not blank out mid-transition.
    */
    const [detailItem, setDetailItem] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const backButtonRef = useRef(null);
    const itemRefs = useRef({});
    const wasDetailOpenRef = useRef(false);

    useEffect(() => {
        if (isDetailOpen === wasDetailOpenRef.current) return;
        wasDetailOpenRef.current = isDetailOpen;

        /*
        Both slides stay in the DOM, so move focus with the panel. Otherwise a
        keyboard user is left on a control that has slid out of view.
        preventScroll matters here: the off-screen slide still overflows the
        viewport, so a scrolling focus would shift the track on top of its own
        translate and push both slides out of sight.
        */
        const target = isDetailOpen
            ? backButtonRef.current
            : itemRefs.current[detailItem && detailItem.key];
        if (target) target.focus({ preventScroll: true });
    }, [isDetailOpen, detailItem]);

    const showDetail = item => {
        setDetailItem(item);
        setIsDetailOpen(true);
    };

    const showList = () => setIsDetailOpen(false);

    return (
        <div
            className={`${classes.container} ${className || ''}`}
            data-testid="understanding-data-sources-section"
        >
            <div
                className={`${classes.slide} ${
                    isDetailOpen ? classes.slideOutLeft : classes.slideIn
                }`}
                aria-hidden={isDetailOpen}
                data-testid="data-labels-list"
            >
                <div className={classes.titleRow}>
                    <Typography component="h3" className={classes.sectionTitle}>
                        {DATA_LABELS_TITLE}
                    </Typography>
                    <IconComponent
                        title={
                            <>
                                {DATA_SOURCES_TOOLTIP_TEXT}
                                <LearnMoreLink
                                    href={DATA_SOURCES_LEARN_MORE_URL}
                                />
                            </>
                        }
                        icon={InfoOutlined}
                        className={classes.infoButton}
                        data-testid="data-sources-info-tooltip"
                    />
                </div>
                <div className={classes.list}>
                    {DATA_SOURCES_ITEMS.map(item => (
                        <DataSourceItem
                            key={item.key}
                            classes={classes}
                            Icon={item.Icon}
                            iconClassName={classes[item.iconClassNameKey]}
                            title={item.title}
                            onSelect={() => showDetail(item)}
                            tabIndex={isDetailOpen ? -1 : 0}
                            buttonRef={node => {
                                itemRefs.current[item.key] = node;
                            }}
                        />
                    ))}
                </div>
            </div>
            <div
                className={`${classes.slide} ${
                    isDetailOpen ? classes.slideIn : classes.slideOutRight
                }`}
                aria-hidden={!isDetailOpen}
                data-testid="data-labels-detail"
            >
                <DataSourceDetail
                    classes={classes}
                    item={detailItem}
                    onBack={showList}
                    tabIndex={isDetailOpen ? 0 : -1}
                    backButtonRef={backButtonRef}
                />
            </div>
        </div>
    );
};

ProductionLocationDetailsDataSourcesInfo.propTypes = {
    classes: PropTypes.object.isRequired,
    className: PropTypes.string,
};

ProductionLocationDetailsDataSourcesInfo.defaultProps = {
    className: '',
};

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
