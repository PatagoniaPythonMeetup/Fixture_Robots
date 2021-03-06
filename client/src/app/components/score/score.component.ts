import { Estado, FixtureService } from '../../../app/fixture.service';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

interface IRobot {
  key: String,
  nombre: String,
  escuela: String,
  encargado: String,
  escudo: String,
  score: Array<Number>
}

@Component({
  selector: 'score',
  templateUrl: './score.component.html',
  styleUrls: ['./score.component.css']
})
export class ScoreComponent implements OnInit {
  @Input() robots: IRobot[] = <IRobot[]>[]
  @Input() ordenable: Boolean = true
  @Input() seleccionable: Boolean = false
  seleccion: Array<String> = <Array<String>>[]
  estado: Estado

  constructor(private fixture: FixtureService) { 
    this.fixture.estado$.subscribe(estado => this.setEstado(estado))
  }

  ngOnInit() {
  }

  setEstado(estado: Estado) {
    this.seleccion = estado.seleccion
    this.estado = estado
  }
  
  checkboxClick(event, robot){
    if(event.target.checked)
      this.seleccion = [...this.seleccion, robot.key];
    else
      this.seleccion = this.seleccion.filter(k => k !== robot.key)
    this.fixture.setRobotsSeleccionados(this.seleccion);
  }
}