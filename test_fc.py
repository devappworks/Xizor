from tools.freedcamp_api import create_freedcamp_task

print(
    create_freedcamp_task(
        title="URL-test from Cursor",
        description="Should return the real FC link",
        assignee_id=1788822,
        priority="P2",
        due_date=None,
    )
)