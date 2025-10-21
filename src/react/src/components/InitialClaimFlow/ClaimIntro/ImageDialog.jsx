import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { claimInfoStyles } from './styles';

const ImageDialog = ({ open, onClose, image, alt, classes }) => (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <IconButton className={classes.closeButton} onClick={onClose}>
            <CloseIcon />
        </IconButton>
        <DialogContent>
            <img src={image} alt={alt} className={classes.dialogImage} />
        </DialogContent>
    </Dialog>
);

ImageDialog.propTypes = {
    open: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    image: PropTypes.string.isRequired,
    alt: PropTypes.string.isRequired,
    classes: PropTypes.object.isRequired,
};

export default withStyles(claimInfoStyles)(ImageDialog);
