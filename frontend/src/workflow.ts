import type {Row} from './domain';

export function replaceLot(lots:Row[],replacement:Row):Row[]{
    return [...lots.filter(l=>l.numero_lote!==replacement.numero_lote),replacement]
        .sort((a,b)=>Number(a.numero_lote)-Number(b.numero_lote));
}

export function operationAnimals(operation:Row,positions:Row[]=[]):string[]{
    return ((operation.lotes as Row[])||[]).flatMap(l=>{
        if(operation.tipo!=='VENTA')return (l.animales as string[])||[];
        return ((l.posiciones as string[])||[]).map(id=>{
            const animal=positions.find(p=>p.id===id)?.animal_id;
            if(typeof animal!=='string')throw new Error('Consulta la composición de todas las posiciones antes de registrar el pesaje.');
            return animal;
        });
    });
}
