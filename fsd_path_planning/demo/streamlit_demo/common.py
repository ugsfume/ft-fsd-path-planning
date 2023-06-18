from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure

from fsd_path_planning.types import FloatArray
from fsd_path_planning.utils.cone_types import ConeTypes
from fsd_path_planning.utils.math_utils import rotate, unit_2d_vector_from_angle


def calculate_pose_triangle_position(
    position: FloatArray, direction: FloatArray, size: float
) -> FloatArray:
    pos_1 = position + direction * size
    pos_2 = position - rotate(direction, np.pi / 2) * size * 0.5
    pos_3 = position - rotate(direction, -np.pi / 2) * size * 0.5
    return np.array([pos_1, pos_2, pos_3])


CONE_TYPE_TO_COLOR = {
    ConeTypes.UNKNOWN: "gray",
    ConeTypes.BLUE: "#00BFFF",
    ConeTypes.YELLOW: "gold",
    ConeTypes.ORANGE_BIG: "orange",
    ConeTypes.ORANGE_SMALL: "orange",
}


def visualize_configuration(
    position: FloatArray,
    direction: FloatArray,
    cones_by_type: list[FloatArray],
    *,
    with_cone_index: bool,
    with_lines: bool,
    do_show: bool,
) -> tuple[Figure, Axes]:
    position_triangle = calculate_pose_triangle_position(position, direction, 1)
    ax = plt.gca()
    ax.fill(*position_triangle.T, color="red", label="Vehicle Pose")

    marker_string = "-o" if with_lines else "o"
    text_offset = 0.5
    for cone_type, cones in zip(ConeTypes, cones_by_type):
        if len(cones) == 0:
            continue
        color = CONE_TYPE_TO_COLOR[cone_type]
        ax.plot(
            *cones.T,
            marker_string,
            color=color,
            label=cone_type.name.replace("_", " ").title(),
        )
        if with_cone_index:
            for i, (x, y) in enumerate(cones):
                ax.text(x - text_offset, y - text_offset, str(i))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("equal")
    # ax.legend(loc="upper left")

    if do_show:
        st.pyplot(plt.gcf())  # type: ignore

    return ax


def get_cones_for_configuration(
    configuration: str, do_shuffle: bool
) -> tuple[FloatArray, FloatArray, list[FloatArray]]:
    rng = np.random.default_rng(0)
    vehicle_position = np.array([0, 0], dtype=float)
    vehicle_direction = np.array([1, 0], dtype=float)
    if configuration == "Straight":
        cones_x = np.arange(-2, 20, 4)
        noise_range = 0.3
        cones_left_y = np.ones(len(cones_x)) * 1.5 + rng.uniform(
            -noise_range, noise_range, len(cones_x)
        )

        cones_right_y = np.ones(len(cones_x)) * -1.5 + rng.uniform(
            -noise_range, noise_range, len(cones_x)
        )

        cones_left = np.column_stack((cones_x, cones_left_y))
        cones_right = np.column_stack((cones_x, cones_right_y))

    elif configuration == "Simple Corner":
        phi_inner = np.arange(0, np.pi / 2, np.pi / 15)
        phi_outer = np.arange(0, np.pi / 2, np.pi / 20)

        points_inner = unit_2d_vector_from_angle(phi_inner) * 9
        points_outer = unit_2d_vector_from_angle(phi_outer) * 12

        center = np.mean((points_inner[:2] + points_outer[:2]) / 2, axis=0)
        points_inner -= center
        points_outer -= center

        rotated_points_inner = rotate(points_inner, -np.pi / 2)
        rotated_points_outer = rotate(points_outer, -np.pi / 2)
        cones_left = rotated_points_inner
        cones_right = rotated_points_outer

    elif configuration == "Corner Missing Blue":
        vehicle_position, vehicle_direction, cones_simple = get_cones_for_configuration(
            "Simple Corner", do_shuffle
        )

        cones_left = cones_simple[ConeTypes.LEFT]
        cones_right = cones_simple[ConeTypes.RIGHT]

        mask_keep = np.ones(len(cones_left), dtype=bool)
        mask_keep[3:7] = False

        cones_left = cones_left[mask_keep]

    elif configuration == "Corner Missing Blue Alt":
        vehicle_position, vehicle_direction, cones_simple = get_cones_for_configuration(
            "Simple Corner", do_shuffle
        )

        cones_left = cones_simple[ConeTypes.LEFT]
        cones_right = cones_simple[ConeTypes.RIGHT]

        mask_keep = np.ones(len(cones_left), dtype=bool)
        mask_keep[1:4] = False

        cones_left = cones_left[mask_keep]

    elif configuration == "Hairpin":
        cones_left = np.array(
            [
                [21.12379456, 29.25],
                [23.81129456, 29.25],
                [26.43629456, 29.25],
                [29.62379456, 29.625],
                [32.43629456, 30.0],
                [35.24879456, 30.9375],
                [37.49879456, 32.25],
                [39.74879456, 33.75],
                [41.81129456, 34.875],
                [44.43629456, 34.875],
                [46.68629456, 33.9375],
                [48.18629456, 32.625],
                [48.93629456, 30.75],
                [49.31129456, 28.125],
                [48.56129456, 24.9375],
                [46.49879456, 22.6875],
                [43.87379456, 21.0],
                [40.87379456, 20.25],
            ]
        )
        cones_right = np.array(
            [
                [23.81129456, 25.875],
                [26.62379456, 26.0625],
                [30.18629456, 26.25],
                [33.37379456, 27.0],
                [36.93629456, 28.3125],
                [39.56129456, 29.4375],
                [41.06129456, 31.125],
                [42.74879456, 31.875],
                [44.62379456, 31.3125],
                [45.56129456, 29.8125],
                [45.74879456, 28.125],
                [45.18629456, 26.25],
                [44.43629456, 24.9375],
                [42.37379456, 24.1875],
                [39.93629456, 23.4375],
                [36.74879456, 23.0625],
                [33.56129456, 22.6875],
                [31.12379456, 22.3125],
                [27.89708838, 22.13631838],
            ]
        )

        vehicle_position = (cones_left[0] + cones_right[0]) / 2

    elif configuration == "Hairpin Extreme":
        vehicle_position, vehicle_direction, cones_simple = get_cones_for_configuration(
            "Hairpin", False
        )

        cones_left = cones_simple[ConeTypes.LEFT]
        cones_right = cones_simple[ConeTypes.RIGHT]

        cones_right[-7:] += [-1, 1]
    elif configuration == "Wrong sort":
        cones_left = np.array(
            [
                [16.31314458, 16.3776545],
                [13.2478797, 14.53239357],
                [11.61994544, 12.77339941],
                [10.38525599, 10.07768147],
                [9.25409952, 7.22949147],
                [9.26290429, 5.16165631],
                [10.22854904, 2.72195712],
                [11.34964389, -0.24510434],
                [11.48446814, -7.86207852],
                [7.80046658, -10.72293007],
            ]
        )
        cones_right = np.zeros((0, 2))

    # shuffle
    if do_shuffle:
        cones_left = cones_left[rng.random(len(cones_left)).argsort()]
        cones_right = cones_right[rng.random(len(cones_right)).argsort()]

    cones = [np.zeros((0, 2)) for _ in ConeTypes]
    # cones = [np.zeros((0, 2)), cones_left, cones_right]
    cones[ConeTypes.LEFT] = cones_left
    cones[ConeTypes.RIGHT] = cones_right
    return vehicle_position, vehicle_direction, cones


def create_animation(frames: list[go.Frame]) -> go.Figure:
    if len(frames) == 0:
        return go.Figure()

    return go.Figure(
        data=frames[0]["data"],
        layout=go.Layout(
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {
                                        "duration": 1000,
                                    },
                                    "transition": {
                                        "duration": 0,
                                    },
                                },
                            ],
                        )
                    ],
                )
            ],
        ),
        frames=frames,
    )
