# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

def copy_attachments(self,cr,uid, ids,src_model,des_record_id, des_model, context=None):
    """ 
    This Function Copy the Attachment for current Record and paste it in Destination model in destination Record ID.

    @param res_model the source model
    @param record_id current record id which is source of attachment
    @param des_record_id the destination record in which the attachment will paste
    @param des_model the destination model
    """

    attachment = self.pool.get('ir.attachment')
    attachment_ids = attachment.search(cr, uid, [('res_model', '=', src_model), ('res_id', '=', ids[0])], context=context)
    new_attachment_ids = []
    for attachment_id in attachment_ids:
        new_attachment_ids.append(attachment.copy(cr, uid, attachment_id, default={'res_id': des_record_id,'res_model':des_model }, context=context))
    return new_attachment_ids

def copy_attachments_set(self,cr,uid, ids,src_model,des_record_id, des_model, context=None):
    """ 
    This Function Copy the Attachment for current Record and paste it in Destination model in destination Record ID.

    @param res_model the source model
    @param record_id current record id which is source of attachment
    @param des_record_id the destination record in which the attachment will paste
    @param des_model the destination model
    """

    attachment = self.pool.get('ir.attachment')
    attachment_ids = attachment.search(cr, uid, [('res_model', '=', src_model), ('res_id', 'in', ids)], context=context)
    new_attachment_ids = []
    for attachment_id in attachment_ids:
        new_attachment_ids.append(attachment.copy(cr, uid, attachment_id, default={'res_id': des_record_id,'res_model':des_model }, context=context))
    return new_attachment_ids

