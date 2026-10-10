TYPE_LABELS = {"lost": "寻物", "found": "招领"}
STATUS_OPTIONS = {
    "lost": ("寻找中", "已找到"),
    "found": ("待认领", "已归还"),
}


def validate_item_form(form, item_type):
    fields = ("name", "category", "location", "event_time", "description", "contact")
    data = {field: form.get(field, "").strip() for field in fields}
    errors = {}

    if item_type not in TYPE_LABELS:
        errors["type"] = "发布类型无效。"
    for field in fields:
        if not data[field]:
            errors[field] = "此项不能为空。"
    if data["description"] and len(data["description"]) < 5:
        errors["description"] = "描述至少需要 5 个字。"
    if data["contact"] and len(data["contact"]) < 3:
        errors["contact"] = "联系方式至少需要 3 个字符。"
    return data, errors
