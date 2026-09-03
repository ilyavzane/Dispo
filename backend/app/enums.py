from enum import StrEnum


class LoadStatus(StrEnum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Roles(StrEnum):
    ADMIN = "admin"
    DRIVER = "driver"
    DISPATCHER = "dispatcher"


class Statuses(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
