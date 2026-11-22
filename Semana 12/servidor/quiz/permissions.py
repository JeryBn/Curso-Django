from rest_framework.permissions import BasePermission

AGENT_GROUP = "agente"


class AgentPermission(BasePermission):
    """Who may do what. This is the SERVER's rule: it holds even if a client misbehaves.

    The rule the lab asks for:
      - a person (user with is_staff) can do anything;
      - a member of the group «agente» can read, create and modify, but NEVER delete;
      - anybody else who is logged in can only read;
      - an unknown method is denied (deny by default).

    The server enforces the role independently of the client and denies unknown methods.
    """

    def has_permission(self, request, view):
        user = request.user
        method = request.method
        if not user or not user.is_authenticated:
            return False
        if method not in {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}:
            return False
        if method in {"GET", "HEAD", "OPTIONS"}:
            return True
        if user.is_staff:
            return True
        if user.groups.filter(name=AGENT_GROUP).exists():
            return method in {"POST", "PUT", "PATCH"}
        return False
