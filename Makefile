# ModelScope-Manager Makefile
.PHONY: help clean

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

help: ## 显示帮助信息
	@echo "$(GREEN)ModelScope-Manager 管理命令$(RESET)"
	@echo ""
	@echo "$(YELLOW)可用命令:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## 清理运行产物
	@echo "$(YELLOW)清理内容...$(RESET)"
	@rm -rf logs output 
	@find . -path ./modelscope_env -prune -o -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '.DS_Store' -delete
	@echo "$(GREEN)清理完成！$(RESET)"
