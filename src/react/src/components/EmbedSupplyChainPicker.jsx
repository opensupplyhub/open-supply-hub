import React from 'react';
import { arrayOf, func, number, object, oneOfType, string } from 'prop-types';
import { connect } from 'react-redux';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import { selectEmbedSupplyChain } from '../actions/filters';
import { getEmbedSupplyChains } from '../util/embeddedMap';
import { makeFilterStyles } from '../util/styles';

const styles = {
    list: {
        display: 'flex',
        flexDirection: 'column',
    },
    card: {
        display: 'flex',
        alignItems: 'center',
        textAlign: 'left',
        marginBottom: '6px',
        padding: '8px 10px',
        border: '1px solid rgb(13, 17, 40)',
        background: 'white',
        fontFamily: 'inherit',
        fontSize: '16px',
        fontWeight: 700,
        cursor: 'pointer',
    },
    cardSelected: {
        background: 'rgb(13, 17, 40)',
        color: 'white',
    },
    swatch: {
        width: '14px',
        height: '14px',
        borderRadius: '50%',
        marginRight: '10px',
        flex: 'none',
        border: '1px solid white',
    },
};

/*
Lets a visitor to an embedded map follow one of the supply chains its
contributor has published. Renders nothing when there are none.
*/
function EmbedSupplyChainPicker({ chains, selectedId, select, classes }) {
    if (!chains.length) return null;

    return (
        <div className="form__field">
            <InputLabel shrink={false} className={classes.inputLabelStyle}>
                Follow a supply chain
            </InputLabel>
            <div style={styles.list}>
                {chains.map(chain => {
                    const isSelected = String(chain.id) === String(selectedId);
                    return (
                        <button
                            key={chain.id}
                            type="button"
                            aria-pressed={isSelected}
                            onClick={() => select(isSelected ? null : chain.id)}
                            style={
                                isSelected
                                    ? { ...styles.card, ...styles.cardSelected }
                                    : styles.card
                            }
                        >
                            <span
                                style={{
                                    ...styles.swatch,
                                    background: chain.color,
                                }}
                            />
                            {chain.name}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

EmbedSupplyChainPicker.propTypes = {
    chains: arrayOf(object),
    selectedId: oneOfType([number, string]),
    select: func.isRequired,
    classes: object.isRequired,
};

EmbedSupplyChainPicker.defaultProps = {
    chains: [],
    selectedId: null,
};

function mapStateToProps({
    embeddedMap: { embed, config },
    filters: { embedSupplyChainId },
}) {
    return {
        chains: getEmbedSupplyChains(embed, config),
        selectedId: embedSupplyChainId,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        select: id => dispatch(selectEmbedSupplyChain(id)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeFilterStyles)(EmbedSupplyChainPicker));
