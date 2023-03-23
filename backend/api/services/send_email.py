from datetime import datetime
import logging
import json

from django.conf import settings

from requests.auth import HTTPBasicAuth
from email.header import Header
from email.utils import formataddr
from api.models.user_profile import UserProfile
from api.models.notification import Notification
from api.models.credit_transfer_statuses import CreditTransferStatuses
from api.models.sales_submission_statuses import SalesSubmissionStatuses
from api.models.model_year_report_statuses import ModelYearReportStatuses
from api.models.vehicle_statuses import VehicleDefinitionStatuses
from api.models.credit_agreement_statuses import CreditAgreementStatuses
from api.models.notification_subscription import NotificationSubscription
from api.models.organization import Organization
import requests
from django.db.models import Q

LOGGER = logging.getLogger(__name__)


def get_email_service_token() -> {}:
    client_id = settings.EMAIL['EMAIL_SERVICE_CLIENT_ID']
    client_secret = settings.EMAIL['EMAIL_SERVICE_CLIENT_SECRET']
    url = settings.EMAIL['CHES_AUTH_URL']
    if not client_id:
        LOGGER.error("Email service client id is not configured")
        return
    if not client_secret:
        LOGGER.error("Email service client secret is not configured")
        return
    if not url:
        LOGGER.error("Common hosted email service authentication url is not configured")
        return
    payload = {"grant_type": "client_credentials"}
    header = {"content-type": "application/x-www-form-urlencoded"}
    try:
        token_rs = requests.post(url, data=payload,
                                 auth=HTTPBasicAuth(client_id, client_secret),
                                 headers=header, verify=True)
        if not token_rs.status_code == 200:
            LOGGER.error("Error: Unexpected response", token_rs.text.encode('utf8'))
            return
        json_obj = token_rs.json()
        return json_obj
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return


def send_email(recipient_email: str, email_type: str, test_info: dict) -> {}:
    sender_email = settings.EMAIL['SENDER_EMAIL']
    sender_name = settings.EMAIL['SENDER_NAME']
    url = settings.EMAIL['CHES_EMAIL_URL']

    if not sender_email:
        LOGGER.error("Sender email address not configured")
        return
    if not url:
        LOGGER.error("CHES email url not configured")
        return
    if not sender_name:
        LOGGER.error("Sender name not configured")
        return
    if not recipient_email:
        LOGGER.error("No recipient email address provided")
        return
    if not email_type:
        LOGGER.error("No email type provided")
        return

    body = """\
                <html>
                <body>
                This email was generated by the Government of B.C. Zero-Emission Vehicle Reporting System.
                <p>A """ + email_type + """  has occurred within the Zero-Emission Vehicle Reporting System that may require your action or be of interest to you, please logon to the system at: <a href ="https://zeroemissionvehicles.gov.bc.ca/">https://zeroemissionvehicles.gov.bc.ca/</a></p>
                <p>You received this email because you subscribed at the site above, to stop receiving these email logon to your account here <a href ="https://zeroemissionvehicles.gov.bc.ca/notifications">https://zeroemissionvehicles.gov.bc.ca/notifications</a></p>
                """
    
    if settings.ENV_NAME != "prod":
        body + """\
            <p>User: """ + test_info['user'] + """</p>
            <p>Action: """ + test_info['action'] + """</p>
            <p>Description: """ + test_info['action_description'] + """</p>
            <p>Time: """ + test_info['time'] + """</p>
            </body>
            </html>
            """
    else:
        body + """\
        </body>
        </html>
        """

    subject = "BC ZEVA Notification"
    bodyType = "html"
    attachment = ""

    token = get_email_service_token()
    if not token or 'access_token' not in token:
        LOGGER.error("No email service token provided", token)
        return
    auth_token = token['access_token']

    sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))

    data = {
            "bcc": recipient_email,
            "bodyType": bodyType,
            "body": body,
            "cc": [],
            "delayTS": 0,
            "encoding": "utf-8",
            "from": sender_info,
            "priority": "normal",
            "subject": subject,
            "to": ["Undisclosed recipients<donotreply@gov.bc.ca>"],
            "tag": "email_1",
            "attachments": attachment
           }

    headers = {"Authorization": 'Bearer ' + auth_token,
               "Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if not response.status_code == 201:
            LOGGER.error("Error: Email failed! %s", response.text.encode('utf8'))
            return

        email_res = response.json()
        if email_res:
            LOGGER.debug("Email sent successfully!", email_res['messages'][0]['msgId'])
            return
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return


def notifications_credit_transfers(transfer: object):
    request_type = 'credit_transfer'
    email_type = '<b>credit transfer update</b>'
    validation_status = transfer.status
    notifications = None
    if validation_status == CreditTransferStatuses.VALIDATED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_TRANSFER_RECORDED_GOVT') |
            Q(notification_code='CREDIT_TRANSFER_RECORDED'))

    elif validation_status == CreditTransferStatuses.SUBMITTED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_TRANSFER_SUBMITTED')

    elif validation_status == CreditTransferStatuses.RECOMMEND_APPROVAL:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_TRANSFER_RECOMMEND_APPROVAL')

    elif validation_status == CreditTransferStatuses.RECOMMEND_REJECTION:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_TRANSFER_RECOMMEND_REJECT')

    elif validation_status == CreditTransferStatuses.APPROVED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_TRANSFER_APPROVED') |
            Q(notification_code='CREDIT_TRANSFER_APPROVED_PARTNER'))

    elif validation_status == CreditTransferStatuses.DISAPPROVED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_TRANSFER_REJECTED_PARTNER')

    elif validation_status == CreditTransferStatuses.RESCINDED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_TRANSFER_RESCINDED') |
            Q(notification_code='CREDIT_TRANSFER_RESCINDED_PARTNER'))

    elif validation_status == CreditTransferStatuses.RESCIND_PRE_APPROVAL:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_TRANSFER_RESCINDED_PARTNER')

    elif validation_status == CreditTransferStatuses.REJECTED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_TRANSFER_REJECTED_GOVT') |
            Q(notification_code='CREDIT_TRANSFER_REJECTED'))

    if notifications:
        subscribed_users(notifications, transfer, request_type, email_type)

def notifications_model_year_report(validation_status, request, previous_status = 'NA'):
    request_type = 'model_year_report'
    email_type = '<b>model year report update</b>'
    notifications = None
    if validation_status == ModelYearReportStatuses.ASSESSED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='MODEL_YEAR_REPORT_ASSESSED_SUPPLIER') |
            Q(notification_code='MODEL_YEAR_REPORT_ASSESSED_GOVT'))
    elif validation_status == ModelYearReportStatuses.SUBMITTED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='MODEL_YEAR_REPORT_SUBMITTED') 
    elif validation_status == ModelYearReportStatuses.RECOMMENDED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='MODEL_YEAR_REPORT_RECOMMENDED') 
    elif validation_status == ModelYearReportStatuses.RETURNED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='MODEL_YEAR_REPORT_RETURNED') 
    elif validation_status == ModelYearReportStatuses.DRAFT.name and previous_status == ModelYearReportStatuses.ASSESSED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='MODEL_YEAR_REPORT_RETURNED') 

    if notifications:
        subscribed_users(notifications, request, request_type, email_type)

def notifications_credit_agreement(agreement: object):
    request_type = 'credit_agreement'
    email_type = '<b>credit agreement update</b>'
    validation_status = agreement.status
    notifications = None
    if validation_status == CreditAgreementStatuses.ISSUED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_AGREEMENT_ISSUED_SUPPLIER') |
            Q(notification_code='CREDIT_AGREEMENT_ISSUED_GOVT'))
    elif validation_status == CreditAgreementStatuses.RECOMMENDED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_AGREEMENT_RECOMMENDED') 
    elif validation_status == CreditAgreementStatuses.RETURNED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_AGREEMENT_RETURNED_WITH_COMMENT') 

    if notifications:
        subscribed_users(notifications, agreement, request_type, email_type)

def notifications_credit_application(submission: object):
    request_type = 'credit_application'
    email_type = '<b>credit application update</b>'
    validation_status = submission.validation_status
    notifications = None
    if validation_status == SalesSubmissionStatuses.VALIDATED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='CREDIT_APPLICATION_ISSUED') |
            Q(notification_code='CREDIT_APPLICATION_ISSUED_GOVT'))

    elif validation_status == SalesSubmissionStatuses.CHECKED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_APPLICATION_CHECKED')

    elif validation_status == SalesSubmissionStatuses.RECOMMEND_APPROVAL:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_APPLICATION_RECOMMEND_APPROVAL')

    elif validation_status == SalesSubmissionStatuses.SUBMITTED:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='CREDIT_APPLICATION_SUBMITTED')

    if notifications:
        subscribed_users(notifications, submission, request_type, email_type)


def notifications_zev_model(request: object, validation_status: str):
    request_type = 'zev_model'
    email_type = '<b>ZEV model update</b>'
    notifications = None
    if validation_status == VehicleDefinitionStatuses.VALIDATED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='ZEV_MODEL_VALIDATED')

    elif validation_status == VehicleDefinitionStatuses.REJECTED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='ZEV_MODEL_REJECTED')

    elif validation_status == VehicleDefinitionStatuses.SUBMITTED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            Q(notification_code='ZEV_MODEL_SUBMITTED') |
            Q(notification_code='ZEV_MODEL_RANGE_REPORT_SUBMITTED'))

    elif validation_status == VehicleDefinitionStatuses.CHANGES_REQUESTED.name:
        notifications = Notification.objects.values_list('id', flat=True).filter(
            notification_code='ZEV_MODEL_RANGE_REPORT_TEST_RESULT_REQUESTED')

    if notifications:
        subscribed_users(notifications, request, request_type, email_type)


"""
Send email to the users based on their notification subscription
"""


def subscribed_users(notifications: list, request: object, request_type: str, email_type: str):
    user_email = None
    test_info = {}
    try:
        subscribed_users = NotificationSubscription.objects.values_list('user_profile_id', flat=True).filter(
          notification__id__in=notifications).filter(
            user_profile__is_active=True
          )
        if subscribed_users:
            govt_org = Organization.objects.filter(is_government=True).first()

            if request_type == 'credit_transfer':
                user_email = UserProfile.objects.values_list('email', flat=True).filter(
                    Q(organization_id__in=[request.debit_from_id,
                                           request.credit_to_id,
                                           govt_org.id]) &
                    Q(id__in=subscribed_users)).exclude(email__isnull=True).exclude(email__exact='').exclude(username=request.update_user)

            else:
                if request_type == 'model_year_report':
                    user_email = UserProfile.objects.values_list('email', flat=True).filter(
                        Q(organization_id__in=[request.user.organization.id,
                                           govt_org.id]) &
                        Q(id__in=subscribed_users)).exclude(email__isnull=True).exclude(email__exact='').exclude(username=request.user.update_user)
                else:        
                    user_email = UserProfile.objects.values_list('email', flat=True).filter(
                        Q(organization_id__in=[request.organization,
                                            govt_org.id]) &
                        Q(id__in=subscribed_users)).exclude(email__isnull=True).exclude(email__exact='').exclude(username=request.update_user)

            notification_object = Notification.objects.filter(id=notifications).first()

            test_info['user'] = request.update_user
            test_info['action'] = notification_object.name
            test_info['action_description'] = notification_object.description
            test_info['time'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
            if user_email:
                send_email(list(user_email), email_type, test_info)
    except Exception as e:
        LOGGER.error('Unable to send email! %s', e)
