"""Tests for SVG generation (SVGBuilder + templates)."""

import copy

import pytest

from generator.config import validate_config
from generator.svg_builder import SVGBuilder


class TestSVGBuilder:
    def test_init(self, svg_builder):
        assert svg_builder.config["username"] == "galaxy-dev"

    def test_render_galaxy_header_valid_svg(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_galaxy_header_contains_name(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert "Nyx Orion" in svg

    def test_galaxy_header_contains_animations(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert "animate" in svg

    def test_render_stats_card_valid_svg(self, svg_builder):
        svg = svg_builder.render_stats_card()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_stats_card_contains_formatted_values(self, svg_builder):
        svg = svg_builder.render_stats_card()
        assert "1.8k" in svg  # commits=1847
        assert "342" in svg   # stars
        assert "156" in svg   # prs

    def test_render_tech_stack_valid_svg(self, svg_builder):
        svg = svg_builder.render_tech_stack()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_tech_stack_contains_language_names(self, svg_builder):
        svg = svg_builder.render_tech_stack()
        assert "Python" in svg
        assert "TypeScript" in svg

    def test_render_projects_constellation_valid_svg(self, svg_builder):
        svg = svg_builder.render_projects_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_projects_constellation_contains_repo_names(self, svg_builder):
        svg = svg_builder.render_projects_constellation()
        assert "nebula-ui" in svg
        assert "stargate-api" in svg


class TestNewTemplates:
    def test_render_contribution_heatmap_valid_svg(self, svg_builder):
        svg = svg_builder.render_contribution_heatmap()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_contribution_heatmap_contains_animation(self, svg_builder):
        svg = svg_builder.render_contribution_heatmap()
        assert "@keyframes" in svg

    def test_contribution_heatmap_contains_title(self, svg_builder):
        svg = svg_builder.render_contribution_heatmap()
        assert "CONTRIBUTION NEBULA" in svg

    def test_render_skill_constellation_valid_svg(self, svg_builder):
        svg = svg_builder.render_skill_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_skill_constellation_contains_tech_names(self, svg_builder):
        svg = svg_builder.render_skill_constellation()
        assert "React" in svg
        assert "TypeScript" in svg

    def test_skill_constellation_contains_group_labels(self, svg_builder):
        svg = svg_builder.render_skill_constellation()
        assert "Frontend" in svg
        assert "Backend" in svg

    def test_render_coding_timeline_valid_svg(self, svg_builder):
        svg = svg_builder.render_coding_timeline()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_coding_timeline_contains_labels(self, svg_builder):
        svg = svg_builder.render_coding_timeline()
        assert "Started React" in svg

    def test_coding_timeline_contains_comet(self, svg_builder):
        svg = svg_builder.render_coding_timeline()
        assert "animateMotion" in svg


class TestEdgeCases:
    def test_empty_projects(self, cfg, sample_stats, sample_languages, sample_contributions):
        cfg["projects"] = []
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, sample_languages, sample_contributions)
        svg = builder.render_projects_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_empty_languages(self, cfg, sample_stats, sample_contributions):
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, {}, sample_contributions)
        svg = builder.render_tech_stack()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_zero_stats(self, cfg, sample_languages, sample_contributions):
        config = validate_config(cfg)
        zero_stats = {"commits": 0, "stars": 0, "prs": 0, "issues": 0, "repos": 0}
        builder = SVGBuilder(config, zero_stats, sample_languages, sample_contributions)
        svg = builder.render_stats_card()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_empty_contributions(self, cfg, sample_stats, sample_languages):
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, sample_languages, {"total_count": 0, "weeks": []})
        svg = builder.render_contribution_heatmap()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")
        assert "No contribution data" in svg

    def test_empty_timeline(self, cfg, sample_stats, sample_languages, sample_contributions):
        cfg["timeline"] = []
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, sample_languages, sample_contributions)
        svg = builder.render_coding_timeline()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")
        assert "No timeline data" in svg

    def test_empty_galaxy_arms_skill_constellation(self, cfg, sample_stats, sample_languages, sample_contributions):
        # Can't have empty galaxy_arms (required by config), but test with minimal
        cfg["galaxy_arms"] = [{"name": "Solo", "color": "synapse_cyan", "items": []}]
        cfg["projects"] = []
        cfg["timeline"] = []
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, sample_languages, sample_contributions)
        svg = builder.render_skill_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")
