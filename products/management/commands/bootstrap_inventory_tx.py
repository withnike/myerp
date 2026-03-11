from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Inventory, InventoryTx


class Command(BaseCommand):
    help = "기존 Inventory.quantity 값을 InventoryTx 초기재고(ADJUST) 로그로 옮깁니다."

    @transaction.atomic
    def handle(self, *args, **options):
        count_created = 0
        count_skipped = 0

        inventories = Inventory.objects.select_related("product", "company").all()

        for inv in inventories:
            # 이미 같은 상품에 ADJUST 로그가 있으면 건너뜀
            exists = InventoryTx.objects.filter(
                company=inv.company,
                product=inv.product,
                tx_type="ADJUST"
            ).exists()

            if exists:
                count_skipped += 1
                continue

            # 현재 Inventory 수량을 초기재고로 기록
            InventoryTx.objects.create(
                company=inv.company,
                product=inv.product,
                tx_type="ADJUST",
                source_id=inv.id,   # Inventory id를 source_id로 사용
                qty_change=inv.quantity,
            )
            count_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"완료: 초기재고 로그 생성 {count_created}건, 건너뜀 {count_skipped}건"
        ))