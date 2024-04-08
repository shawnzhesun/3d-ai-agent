from datetime import datetime
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.users.item.calendar_view.calendar_view_request_builder import (
    CalendarViewRequestBuilder)

class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)

    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token

    async def greet_user(self):
        user = await self.get_user()
        if user:
            print('Hello,', user.display_name)
            # For Work/school accounts, email is in mail property
            # Personal accounts, email is in userPrincipalName
            print('Email:', user.mail or user.user_principal_name, '\n')

    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.user_client.me.get(request_configuration=request_config)
        return user

    async def get_inbox(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters= query_params
        )

        messages = await self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages

    async def list_inbox(self):
        message_page = await self.get_inbox()
        if message_page and message_page.value:
            # Output each message's details
            for message in message_page.value:
                print('Message:', message.subject)
                if (
                    message.from_ and
                    message.from_.email_address
                ):
                    print('  From:', message.from_.email_address.name or 'NONE')
                else:
                    print('  From: NONE')
                print('  Status:', 'Read' if message.is_read else 'Unread')
                print('  Received:', message.received_date_time)

            # If @odata.nextLink is present
            more_available = message_page.odata_next_link is not None
            print('\nMore messages available?', more_available, '\n')

    async def get_calendar_events(self, start: datetime, end: datetime):
        # Format start and end times to ISO 8601 format
        start_time = start.isoformat()
        end_time = end.isoformat()

        query_params = CalendarViewRequestBuilder.CalendarViewRequestBuilderListQueryParameters(
            start_date_time=start_time,
            end_date_time=end_time,
            select=['subject', 'organizer', 'start', 'end', 'location']
        )

        request_config = CalendarViewRequestBuilder.CalendarViewRequestBuilderListRequestConfiguration(
            query_parameters=query_params
        )

        events = await self.user_client.me.calendar_view.list(
            start_date_time=start_time,
            end_date_time=end_time,
            request_configuration=request_config
        )

        return events

    async def list_calendar_events(self, start: datetime, end: datetime):
        events_page = await self.get_calendar_events(start, end)
        if events_page and events_page.value:
            for event in events_page.value:
                print('Event:', event.subject)
                if event.organizer and event.organizer.email_address:
                    print('  Organizer:', event.organizer.email_address.name)
                if event.start and event.end:
                    print('  Starts:', event.start.date_time, 'Ends:', event.end.date_time)
                if event.location:
                    print('  Location:', event.location.display_name)
            # Check for more events
            more_available = events_page.odata_next_link is not None
            print('\nMore events available?', more_available, '\n')
