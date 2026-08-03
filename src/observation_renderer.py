from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


SUPPORTED_OBSERVATION_LANGUAGES = ("en", "zh-CN", "es")


def validate_observation_language(language: str) -> None:
    if language not in SUPPORTED_OBSERVATION_LANGUAGES:
        available = ", ".join(SUPPORTED_OBSERVATION_LANGUAGES)
        raise ValueError(
            f"Unsupported observation language {language!r}. "
            f"Available languages: {available}."
        )


def render_horizon_observation(
    *,
    language: str,
    done: bool,
    game_id: int | None = None,
    n_games: int | None = None,
    trial_number: int | None = None,
    total_trials: int | None = None,
    choices_remaining: int | None = None,
    rewards_a: Sequence[int] = (),
    rewards_b: Sequence[int] = (),
    forced_target: str | None = None,
) -> str:
    validate_observation_language(language)
    if done:
        return {
            "en": "The two-option reward task run is complete.",
            "zh-CN": "双选项奖励任务已完成。",
            "es": "La ejecución de la tarea de recompensa con dos opciones ha finalizado.",
        }[language]

    if language == "zh-CN":
        mode = (
            f"强制选择：请选择 {forced_target}。"
            if forced_target is not None
            else "自由选择：请选择 A 或 B。"
        )
        return "\n".join(
            [
                f"第 {game_id} 个游戏，共 {n_games} 个",
                f"第 {trial_number} 回合，共 {total_trials} 回合",
                f"当前游戏剩余选择次数：{choices_remaining}",
                f"A 已观察到的奖励：{list(rewards_a)}",
                f"B 已观察到的奖励：{list(rewards_b)}",
                mode,
            ]
        )
    if language == "es":
        mode = (
            f"Elección forzada: elige {forced_target}."
            if forced_target is not None
            else "Elección libre: elige A o B."
        )
        return "\n".join(
            [
                f"Juego {game_id} de {n_games}",
                f"Turno {trial_number} de {total_trials}",
                f"Elecciones restantes en este juego: {choices_remaining}",
                f"Recompensas observadas de A: {list(rewards_a)}",
                f"Recompensas observadas de B: {list(rewards_b)}",
                mode,
            ]
        )

    mode = (
        f"Forced choice: choose {forced_target}."
        if forced_target is not None
        else "Free choice: choose A or B."
    )
    return "\n".join(
        [
            f"Game {game_id} of {n_games}",
            f"Trial {trial_number} of {total_trials}",
            f"Choices remaining in this game: {choices_remaining}",
            f"Observed rewards for A: {list(rewards_a)}",
            f"Observed rewards for B: {list(rewards_b)}",
            mode,
        ]
    )


def render_igt_observation(
    *,
    language: str,
    done: bool,
    current_trial: int | None = None,
    n_trials: int | None = None,
    cumulative_score: int | None = None,
    records: Sequence[Mapping[str, Any]] = (),
    decks: Iterable[str] = ("A", "B", "C", "D"),
) -> str:
    validate_observation_language(language)
    if done:
        return {
            "en": "The four-deck reward task run is complete.",
            "zh-CN": "四牌组奖励任务已完成。",
            "es": "La ejecución de la tarea de recompensa con cuatro mazos ha finalizado.",
        }[language]

    if language == "zh-CN":
        lines = [
            f"第 {current_trial} 回合，共 {n_trials} 回合",
            f"当前累计得分：{cumulative_score}",
        ]
        if records:
            lines.extend(_igt_history_zh(records, decks))
        lines.append("可选牌组：A, B, C, D")
        return "\n".join(lines)
    if language == "es":
        lines = [
            f"Turno {current_trial} de {n_trials}",
            f"Puntuación acumulada actual: {cumulative_score}",
        ]
        if records:
            lines.extend(_igt_history_es(records, decks))
        lines.append("Mazos disponibles: A, B, C, D")
        return "\n".join(lines)

    lines = [
        f"Trial {current_trial} of {n_trials}",
        f"Current cumulative score: {cumulative_score}",
    ]
    if records:
        lines.extend(_igt_history_en(records, decks))
    lines.append("Available decks: A, B, C, D")
    return "\n".join(lines)


def _igt_deck_stats(
    records: Sequence[Mapping[str, Any]],
    deck: str,
) -> tuple[int, int, float]:
    deck_records = [record for record in records if record["deck"] == deck]
    total_net = sum(int(record["net_outcome"]) for record in deck_records)
    average_net = total_net / len(deck_records) if deck_records else 0.0
    return len(deck_records), total_net, average_net


def _igt_history_en(
    records: Sequence[Mapping[str, Any]],
    decks: Iterable[str],
) -> list[str]:
    previous = records[-1]
    lines = [
        "",
        "Previous trial:",
        f"Choice: {previous['deck']}",
        f"Reward: {previous['reward']}",
        f"Loss: {previous['loss']}",
        f"Net outcome: {previous['net_outcome']}",
        "",
        "Deck history summary:",
    ]
    for deck in decks:
        count, total_net, average_net = _igt_deck_stats(records, deck)
        lines.append(
            f"Deck {deck}: selected {count} times, total net outcome {total_net}, "
            f"average net outcome {average_net:.2f}"
        )
    lines.extend(["", "Recent choices and outcomes:"])
    for record in records[-5:]:
        lines.append(
            f"Trial {record['trial_number']}: {record['deck']}, "
            f"reward {record['reward']}, loss {record['loss']}, "
            f"net {record['net_outcome']}"
        )
    return lines


def _igt_history_zh(
    records: Sequence[Mapping[str, Any]],
    decks: Iterable[str],
) -> list[str]:
    previous = records[-1]
    lines = [
        "",
        "上一回合：",
        f"选择：{previous['deck']}",
        f"奖励：{previous['reward']}",
        f"损失：{previous['loss']}",
        f"净结果：{previous['net_outcome']}",
        "",
        "牌组历史汇总：",
    ]
    for deck in decks:
        count, total_net, average_net = _igt_deck_stats(records, deck)
        lines.append(
            f"牌组 {deck}：已选择 {count} 次，净结果合计 {total_net}，"
            f"平均净结果 {average_net:.2f}"
        )
    lines.extend(["", "最近的选择和结果："])
    for record in records[-5:]:
        lines.append(
            f"第 {record['trial_number']} 回合：{record['deck']}，"
            f"奖励 {record['reward']}，损失 {record['loss']}，"
            f"净结果 {record['net_outcome']}"
        )
    return lines


def _igt_history_es(
    records: Sequence[Mapping[str, Any]],
    decks: Iterable[str],
) -> list[str]:
    previous = records[-1]
    lines = [
        "",
        "Turno anterior:",
        f"Elección: {previous['deck']}",
        f"Recompensa: {previous['reward']}",
        f"Pérdida: {previous['loss']}",
        f"Resultado neto: {previous['net_outcome']}",
        "",
        "Resumen del historial de mazos:",
    ]
    for deck in decks:
        count, total_net, average_net = _igt_deck_stats(records, deck)
        lines.append(
            f"Mazo {deck}: seleccionado {count} veces, resultado neto total "
            f"{total_net}, resultado neto medio {average_net:.2f}"
        )
    lines.extend(["", "Elecciones y resultados recientes:"])
    for record in records[-5:]:
        lines.append(
            f"Turno {record['trial_number']}: {record['deck']}, "
            f"recompensa {record['reward']}, pérdida {record['loss']}, "
            f"resultado neto {record['net_outcome']}"
        )
    return lines


def render_bart_observation(
    *,
    language: str,
    done: bool,
    current_balloon: int | None = None,
    n_balloons: int | None = None,
    block_number: int | None = None,
    current_pump_count: int | None = None,
    temporary_earning: float | None = None,
    total_earning: float | None = None,
    balloon_records: Sequence[Mapping[str, Any]] = (),
) -> str:
    validate_observation_language(language)
    if done:
        return {
            "en": "The balloon earnings task run is complete.",
            "zh-CN": "气球收益任务已完成。",
            "es": "La ejecución de la tarea de ganancias con globos ha finalizado.",
        }[language]

    if language == "zh-CN":
        lines = [
            f"第 {current_balloon} 个气球，共 {n_balloons} 个",
            f"区块编号：{block_number}",
            f"当前充气次数：{current_pump_count}",
            f"临时收益：{temporary_earning:.2f}",
            f"总收益：{total_earning:.2f}",
        ]
        if balloon_records:
            lines.extend(_bart_history_zh(balloon_records))
        lines.append("可选操作：PUMP, CASH_OUT")
        return "\n".join(lines)
    if language == "es":
        lines = [
            f"Globo {current_balloon} de {n_balloons}",
            f"Número de bloque: {block_number}",
            f"Número actual de inflados: {current_pump_count}",
            f"Ganancia temporal: {temporary_earning:.2f}",
            f"Ganancia total: {total_earning:.2f}",
        ]
        if balloon_records:
            lines.extend(_bart_history_es(balloon_records))
        lines.append("Acciones disponibles: PUMP, CASH_OUT")
        return "\n".join(lines)

    lines = [
        f"Balloon {current_balloon} of {n_balloons}",
        f"Block number: {block_number}",
        f"Current pump count: {current_pump_count}",
        f"Temporary earning: {temporary_earning:.2f}",
        f"Total earning: {total_earning:.2f}",
    ]
    if balloon_records:
        lines.extend(_bart_history_en(balloon_records))
    lines.append("Available actions: PUMP, CASH_OUT")
    return "\n".join(lines)


def _bart_history_values(
    records: Sequence[Mapping[str, Any]],
) -> tuple[Mapping[str, Any], int, float]:
    previous = records[-1]
    exploded_count = sum(1 for record in records if record["exploded"])
    pump_counts = [int(record["final_pump_count"]) for record in records]
    average_pumps = sum(pump_counts) / len(pump_counts) if pump_counts else 0.0
    return previous, exploded_count, average_pumps


def _bart_history_en(records: Sequence[Mapping[str, Any]]) -> list[str]:
    previous, exploded_count, average_pumps = _bart_history_values(records)
    outcome = "exploded" if previous["exploded"] else "cashed out"
    lines = [
        "",
        "Previous balloon:",
        f"Final pump count: {previous['final_pump_count']}",
        f"Outcome: {outcome}",
        f"Earning: {previous['earning_from_balloon']:.2f}",
        "",
        "Recent balloon outcomes:",
    ]
    for record in records[-5:]:
        record_outcome = "exploded" if record["exploded"] else "cashed out"
        lines.append(
            f"Balloon {record['balloon_id']}: {record['final_pump_count']} pumps, "
            f"{record_outcome}, earning {record['earning_from_balloon']:.2f}"
        )
    lines.extend(
        [
            "",
            "Overall so far:",
            f"Balloons completed: {len(records)}",
            f"Explosions: {exploded_count}",
            f"Average pumps: {average_pumps:.2f}",
        ]
    )
    return lines


def _bart_history_zh(records: Sequence[Mapping[str, Any]]) -> list[str]:
    previous, exploded_count, average_pumps = _bart_history_values(records)
    outcome = "爆炸" if previous["exploded"] else "已兑现"
    lines = [
        "",
        "上一个气球：",
        f"最终充气次数：{previous['final_pump_count']}",
        f"结果：{outcome}",
        f"收益：{previous['earning_from_balloon']:.2f}",
        "",
        "最近的气球结果：",
    ]
    for record in records[-5:]:
        record_outcome = "爆炸" if record["exploded"] else "已兑现"
        lines.append(
            f"气球 {record['balloon_id']}：充气 {record['final_pump_count']} 次，"
            f"{record_outcome}，收益 {record['earning_from_balloon']:.2f}"
        )
    lines.extend(
        [
            "",
            "当前总体情况：",
            f"已完成气球数：{len(records)}",
            f"爆炸次数：{exploded_count}",
            f"平均充气次数：{average_pumps:.2f}",
        ]
    )
    return lines


def _bart_history_es(records: Sequence[Mapping[str, Any]]) -> list[str]:
    previous, exploded_count, average_pumps = _bart_history_values(records)
    outcome = "explotó" if previous["exploded"] else "cobrado"
    lines = [
        "",
        "Globo anterior:",
        f"Número final de inflados: {previous['final_pump_count']}",
        f"Resultado: {outcome}",
        f"Ganancia: {previous['earning_from_balloon']:.2f}",
        "",
        "Resultados recientes de globos:",
    ]
    for record in records[-5:]:
        record_outcome = "explotó" if record["exploded"] else "cobrado"
        lines.append(
            f"Globo {record['balloon_id']}: {record['final_pump_count']} inflados, "
            f"{record_outcome}, ganancia {record['earning_from_balloon']:.2f}"
        )
    lines.extend(
        [
            "",
            "Resumen hasta el momento:",
            f"Globos completados: {len(records)}",
            f"Explosiones: {exploded_count}",
            f"Media de inflados: {average_pumps:.2f}",
        ]
    )
    return lines
