"""
Phase 4: Controller + View 레이어 테스트
계층 경계 규칙 검증 + 핵심 동작 검증
"""
import pytest
import io
from unittest.mock import patch, MagicMock
from datetime import datetime


# ─── 계층 경계 규칙 검증 ────────────────────────────────────────────

class TestLayerBoundaryRules:
    """controller/view/service/repository/model 계층 간 import 규칙 검증."""

    def test_model_does_not_import_from_other_layers(self):
        """model 레이어는 다른 레이어를 import하지 않는다."""
        import ast, os
        model_dir = "model"
        forbidden = {"service", "repository", "controller", "view"}
        for fname in os.listdir(model_dir):
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            with open(os.path.join(model_dir, fname), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        top = node.module.split(".")[0]
                        assert top not in forbidden, \
                            f"model/{fname} imports from forbidden layer '{top}'"

    def test_view_does_not_import_from_model_or_controller(self):
        """view 레이어는 model, controller를 import하지 않는다."""
        import ast, os
        view_dir = "view"
        if not os.path.exists(view_dir):
            pytest.skip("view 디렉토리 없음")
        forbidden = {"controller", "model"}
        for fname in os.listdir(view_dir):
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            with open(os.path.join(view_dir, fname), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    top = node.module.split(".")[0]
                    assert top not in forbidden, \
                        f"view/{fname} imports from forbidden layer '{top}'"

    def test_service_does_not_import_from_controller_or_view(self):
        """service 레이어는 controller, view를 import하지 않는다."""
        import ast, os
        svc_dir = "service"
        forbidden = {"controller", "view"}
        for fname in os.listdir(svc_dir):
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            with open(os.path.join(svc_dir, fname), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    top = node.module.split(".")[0]
                    assert top not in forbidden, \
                        f"service/{fname} imports from forbidden layer '{top}'"

    def test_repository_does_not_import_from_service_controller_view(self):
        """repository 레이어는 service, controller, view를 import하지 않는다."""
        import ast, os
        repo_dir = "repository"
        forbidden = {"service", "controller", "view"}
        for fname in os.listdir(repo_dir):
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            with open(os.path.join(repo_dir, fname), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    top = node.module.split(".")[0]
                    assert top not in forbidden, \
                        f"repository/{fname} imports from forbidden layer '{top}'"


# ─── ConsoleView ────────────────────────────────────────────────────

class TestConsoleView:

    def test_print_title_outputs_system_name(self, capsys):
        from view.console_view import ConsoleView
        v = ConsoleView()
        v.print_title()
        out = capsys.readouterr().out
        assert "반도체 시료 생산주문관리 시스템" in out

    def test_print_success_message(self, capsys):
        from view.console_view import ConsoleView
        v = ConsoleView()
        v.print_success("작업 완료")
        out = capsys.readouterr().out
        assert "작업 완료" in out

    def test_print_error_message(self, capsys):
        from view.console_view import ConsoleView
        v = ConsoleView()
        v.print_error("오류 발생")
        out = capsys.readouterr().out
        assert "오류 발생" in out

    def test_print_menu_displays_all_options(self, capsys):
        from view.console_view import ConsoleView
        v = ConsoleView()
        v.print_main_menu(total_samples=3, total_stock=150, active_orders=5, waiting_jobs=2)
        out = capsys.readouterr().out
        assert "[1]" in out
        assert "[2]" in out
        assert "[3]" in out
        assert "[4]" in out
        assert "[5]" in out
        assert "[6]" in out
        assert "[0]" in out


# ─── SampleView ─────────────────────────────────────────────────────

class TestSampleView:

    def _make_sample(self, id="S001", name="시료A", stock=100):
        from model.sample import Sample
        return Sample(id=id, name=name, avg_production_time=30.0, yield_rate=0.92, stock=stock)

    def test_print_sample_list_shows_headers(self, capsys):
        from view.sample_view import SampleView
        v = SampleView()
        v.print_sample_list([self._make_sample()])
        out = capsys.readouterr().out
        # 시료 ID, 이름, 재고 등 헤더가 있어야 함
        assert "S001" in out
        assert "시료A" in out

    def test_print_sample_list_empty_shows_message(self, capsys):
        from view.sample_view import SampleView
        v = SampleView()
        v.print_sample_list([])
        out = capsys.readouterr().out
        assert len(out) > 0  # 빈 목록 안내 메시지


# ─── OrderView ──────────────────────────────────────────────────────

class TestOrderView:

    def _make_order(self, status=None):
        from model.order import Order, OrderStatus
        now = datetime.now()
        return Order(
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="시료A",
            customer_name="고객A",
            quantity=50,
            status=status or OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )

    def test_print_order_list_shows_order_id(self, capsys):
        from view.order_view import OrderView
        v = OrderView()
        v.print_order_list([self._make_order()])
        out = capsys.readouterr().out
        assert "ORD-20260508-0001" in out

    def test_print_order_detail_shows_customer(self, capsys):
        from view.order_view import OrderView
        v = OrderView()
        v.print_order_detail(self._make_order())
        out = capsys.readouterr().out
        assert "고객A" in out


# ─── SampleController — input/output 분리 검증 ──────────────────────

class TestSampleController:

    def _make_controller(self, tmp_path):
        from repository.sample_repository import SampleRepository
        from service.sample_service import SampleService
        from view.sample_view import SampleView
        from controller.sample_controller import SampleController
        repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
        svc = SampleService(sample_repo=repo)
        view = SampleView()
        return SampleController(sample_service=svc, view=view)

    def test_sample_controller_does_not_call_print_directly(self, tmp_path):
        """controller는 print()를 직접 호출하지 않고 view를 통해서만 출력한다."""
        import ast, os
        with open("controller/sample_controller.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    pytest.fail("SampleController directly calls print() — use view instead")

    def test_register_sample_via_controller(self, tmp_path):
        ctrl = self._make_controller(tmp_path)
        inputs = iter(["S001", "테스트 시료", "30.0", "0.92", "100"])
        with patch("builtins.input", side_effect=inputs):
            ctrl.register_sample()
        from repository.sample_repository import SampleRepository
        repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
        assert repo.find_by_id("S001") is not None

    def test_list_samples_via_controller(self, tmp_path, capsys):
        ctrl = self._make_controller(tmp_path)
        inputs_reg = iter(["S001", "시료A", "30.0", "0.92", "100"])
        with patch("builtins.input", side_effect=inputs_reg):
            ctrl.register_sample()
        ctrl.list_samples()
        out = capsys.readouterr().out
        assert "S001" in out


# ─── MainController ─────────────────────────────────────────────────

class TestMainController:

    def _make_all_services(self, tmp_path):
        from repository.sample_repository import SampleRepository
        from repository.order_repository import OrderRepository
        from repository.production_repository import ProductionRepository
        from service.sample_service import SampleService
        from service.production_service import ProductionService
        from service.order_service import OrderService
        from service.release_service import ReleaseService

        sample_repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
        order_repo = OrderRepository(file_path=str(tmp_path / "orders.json"))
        prod_repo = ProductionRepository(file_path=str(tmp_path / "jobs.json"))

        sample_svc = SampleService(sample_repo=sample_repo)
        prod_svc = ProductionService(prod_repo=prod_repo, order_repo=order_repo, sample_repo=sample_repo)
        order_svc = OrderService(order_repo=order_repo, sample_repo=sample_repo, production_service=prod_svc)
        release_svc = ReleaseService(order_repo=order_repo, sample_repo=sample_repo)
        return sample_svc, order_svc, prod_svc, release_svc

    def test_main_controller_exits_on_zero(self, tmp_path):
        from controller.main_controller import MainController
        svcs = self._make_all_services(tmp_path)
        ctrl = MainController(*svcs)
        with patch("builtins.input", return_value="0"):
            ctrl.run()  # 무한루프 없이 종료

    def test_main_controller_shows_menu(self, tmp_path, capsys):
        from controller.main_controller import MainController
        svcs = self._make_all_services(tmp_path)
        ctrl = MainController(*svcs)
        with patch("builtins.input", side_effect=["0"]):
            ctrl.run()
        out = capsys.readouterr().out
        assert "[1]" in out
        assert "[0]" in out
