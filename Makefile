.PHONY: test test-cov install run

# 安裝測試相關套件
install:
	pip install -r requirements.txt
	pip install pytest pytest-cov

# 執行所有測試（自動設 PYTHONPATH）
test:
	PYTHONPATH=. pytest tests/

# 只測試 tests/ 目錄
test-only:
	PYTHONPATH=. pytest tests/

# 產生測試覆蓋率報告
test-cov:
	PYTHONPATH=. pytest --cov=src

# 顯示詳細測試過程
test-verbose:
	PYTHONPATH=. pytest -v 

run:
	@echo "關閉殘留的 serve 進程..."
	@pkill -f serve || true
	@echo "啟動後端 (API)..."
	@python server.py &
	@echo "啟動前端 (http://localhost:5173)..."
	@cd frontend && serve -l 5173 &
	@wait 